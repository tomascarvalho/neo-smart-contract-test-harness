"""
Events include Runtime.Notify, Runtime.Log, Storage.*, Execution.Success
and several more. See the documentation here:

http://neo-python.readthedocs.io/en/latest/smartcontracts.html
"""
from __future__ import absolute_import, unicode_literals

import threading
from time import sleep

from logzero import logger
from neo.Core.Blockchain import Blockchain
from neo.EventHub import events, SmartContractEvent
from neo.Implementations.Blockchains.LevelDB.LevelDBBlockchain import LevelDBBlockchain
from neo.Implementations.Notifications.LevelDB.NotificationDB import NotificationDB
from neo.Network.NodeLeader import NodeLeader
from neo.Settings import settings
from twisted.internet import reactor, task

from exceptions import NodeBlockingException
from tasks import handle_event
from tasks import app as celery_app

__all__ = ('celery_app',)

@events.on(SmartContractEvent.RUNTIME_NOTIFY)
@events.on(SmartContractEvent.RUNTIME_LOG)
@events.on(SmartContractEvent.EXECUTION_SUCCESS)
@events.on(SmartContractEvent.EXECUTION_FAIL)
@events.on(SmartContractEvent.EXECUTION_INVOKE)
@events.on(SmartContractEvent.VERIFICATION_FAIL)
@events.on(SmartContractEvent.VERIFICATION_SUCCESS)
@events.on(SmartContractEvent.STORAGE_DELETE)
@events.on(SmartContractEvent.STORAGE_GET)
@events.on(SmartContractEvent.STORAGE_PUT)
@events.on(SmartContractEvent.CONTRACT_CREATED)
@events.on(SmartContractEvent.CONTRACT_DESTROY)
@events.on(SmartContractEvent.CONTRACT_MIGRATED)
def call_on_event(sc_event):
    """ Is called whenever an event occurs and puts event into queue.

    Event types can be found at:
    https://neo-python.readthedocs.io/en/latest/neo/SmartContract/smartcontracts.html#event-types
    """
    if settings.is_mainnet:
        network = 'mainnet'
    elif settings.is_testnet:
        network = 'testnet' 
    else:
        network = 'privnet'

    try:
        event_data = {
            'event_type': sc_event.event_type,
            'contract_hash': str(sc_event.contract_hash),
            'tx_hash': str(sc_event.tx_hash),
            'block_number': sc_event.block_number,
            'event_payload': sc_event.event_payload.ToJson(),
            'execution_success': sc_event.execution_success,
            'test_mode': sc_event.test_mode,
            'extra': {'network': network}
        }
        logger.info(event_data)
        handle_event.delay(event_data)
    except Exception as e:
        logger.warning(e)


def custom_background_code():
    """ Custom code run in a background thread. Prints the current block height.

    This function is run in a daemonized thread, which means it can be instantly killed at any
    moment, whenever the main thread quits. If you need more safety, don't use a  daemonized
    thread and handle exiting this thread in another way (eg. with signals and events).

    Raises an exception every 5 minutes the block count is blocked and restarts the node
    """
    if settings.is_mainnet:
        network = 'Mainnet'
    elif settings.is_testnet:
        network = 'Testnet' 
    else:
        network = 'Privnet'
    counter = 0
    previous_block_count = 0

    while True:
        try:
            logger.info(f"Block {str(Blockchain.Default().Height)} / {str(Blockchain.Default().HeaderHeight)}")
            logger.info(f"Connected to {len(NodeLeader.Instance().Peers)} peers.")
            for peer in NodeLeader.Instance().Peers:
                logger.info(peer.Address)
            logger.info("\n")
            if previous_block_count == Blockchain.Default().Height:
                counter += 1
                if counter % 5 == 0:
                    error = '{} Node is blocking'.format(network)
                    message = 'Node is blocking at block: {}. Connected peers: {}. Attempting restart.'
                    message = message.format(Blockchain.Default().Height, len(NodeLeader.Instance().Peers))
                    raise NodeBlockingException(error, message)
            else:
                previous_block_count = Blockchain.Default().Height
                counter = 0
        except Exception as e:
            logger.warning(e)
            NodeLeader.Instance().Shutdown()
            NodeLeader.Instance().Start()
            counter = 0
        sleep(15)


def main(**options):
    settings.setup_privnet()

    # Setup the blockchain
    blockchain = LevelDBBlockchain(settings.chain_leveldb_path)
    Blockchain.RegisterBlockchain(blockchain)
    dbloop = task.LoopingCall(Blockchain.Default().PersistBlocks)
    dbloop.start(.1)
    NodeLeader.Instance().Start()

    # Setup Notifications Database
    NotificationDB.instance().start()

    # Disable smart contract events for external smart contracts
    settings.set_log_smart_contract_events(False)

    # Start a thread with custom code
    d = threading.Thread(target=custom_background_code)
    d.setDaemon(True)  # daemonizing the thread will kill it when the main thread is quit
    d.start()

    # Run all the things (blocking call)
    logger.info("Everything setup and running. Waiting for events...")
    reactor.run()
    logger.info("Shutting down.")
    logger.info("Closing databases...")
    NotificationDB.close()
    Blockchain.Default().Dispose()
    NodeLeader.Instance().Shutdown()


if __name__ == "__main__":
    main()
