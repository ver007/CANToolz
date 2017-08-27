import time
import unittest

from cantoolz.engine import CANSploit


class TestGenReplay(unittest.TestCase):

    def tearDown(self):
        self.CANEngine.stop_loop()
        self.CANEngine = None
        print("stopped")

    def test_replay(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config("tests/configurations/conf_gen_replay.py")
        self.CANEngine.start_loop()
        time.sleep(2)
        # Disable mod_stat module.
        self.CANEngine.call_module(2, 's')
        # Get number of loaded packets by gen_replay.
        num = self.CANEngine.call_module(1, 'p')
        self.assertTrue(0 <= num.find("Loaded packets: 0"), "Should be 0 packets")
        time.sleep(3)
        # Enable sniffing for gen_replay to capture new packets.
        self.CANEngine.call_module(1, 'g')
        # Generate a few packets on the bus.
        self.CANEngine.call_module(0, 't 4:8:1122334411111111')
        time.sleep(1)
        self.CANEngine.call_module(0, 't 4:8:1122334411111111')
        time.sleep(1)
        self.CANEngine.call_module(0, 't 666:8:1122334411111111')
        time.sleep(1)
        self.CANEngine.call_module(0, 't 5:8:1122334411111111')
        time.sleep(3)
        # Get number of loaded packets by gen_replay.
        num = self.CANEngine.call_module(1, 'p')
        self.assertTrue(0 <= num.find("Loaded packets: 4"), "Should be 4 packets")

        # Enable sniffing for gen_replay to capture new packets.
        self.CANEngine.call_module(1, 'g')
        # Save range of capture packets.
        ret = self.CANEngine.call_module(1, 'd 0-4')
        time.sleep(1)
        print(ret)
        # Enable mod_stat module.
        self.CANEngine.call_module(2, 's')
        time.sleep(1)
        # Replay a range of CAN messages.
        self.CANEngine.call_module(1, 'r 0-4')
        time.sleep(5)
        # Clear gen_replay table.
        self.CANEngine.call_module(1, 'c')
        time.sleep(1)
        # Print count of loaded packets.
        num = self.CANEngine.call_module(1, 'p')
        time.sleep(1)
        self.assertTrue(0 <= num.find("Loaded packets: 0"), "Should be 0 packets")
        index = 2
        # Get table of CAN messages sniffed by mod_stats
        ret = self.CANEngine.call_module(2, 'p')
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        print(ret)
        time.sleep(1)
        self.assertTrue(len(_bodyList) == 3, "Should be 3 groups found")

    def test_replay2(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config('tests/configurations/conf_gen_replay2.py')
        self.CANEngine.start_loop()
        # Get number of loaded packets by gen_replay.
        num = self.CANEngine.call_module(1, 'p')
        time.sleep(1)
        self.assertTrue(0 <= num.find("Loaded packets: 4"), "Should be 4 packets")
        index = 2
        # Get table of CAN messages sniffed by mod_stats
        self.CANEngine.call_module(2, 'p')
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(len(_bodyList) == 0, "Should be 0 packets sent")
        # Replay a range of CAN messages.
        self.CANEngine.call_module(1, 'r 2-4')
        time.sleep(3)
        # Get table of CAN messages sniffed by mod_stats
        ret = self.CANEngine.call_module(2, 'p')
        print(ret)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList

        self.assertTrue(2 == len(_bodyList), "Should be 2 packets sent")
        self.assertTrue(666 in _bodyList, "ID 666 should be dound")
        self.assertTrue(5 in _bodyList, "ID 5 should be found")
        self.assertFalse(4 in _bodyList, "ID 4 should not be found ")
        # Dump mod_stat buffer to file.
        self.CANEngine.call_module(2, 'r tests/data/new.save')
        # Load file to gen_replay buffer.
        self.CANEngine.call_module(1, 'l tests/data/new.save')
        # Get number of loaded packets by gen_replay.
        ret = self.CANEngine.call_module(1, 'p')
        print(ret)
        self.assertTrue(0 <= ret.find("Loaded packets: 6"), "Should be 26 packets")
        # Clear gen_replay table.
        self.CANEngine.call_module(1, 'c')
        # Load file to gen_replay buffer.
        self.CANEngine.call_module(1, 'l tests/data/new.save')
        # Get number of loaded packets by gen_replay.
        ret = self.CANEngine.call_module(1, 'p')
        print(ret)
        self.assertTrue(0 <= ret.find("Loaded packets: 2"), "Should be 2 packets")

    def test_replay_uds(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config('tests/configurations/conf_gen_replay_uds.py')
        self.CANEngine.start_loop()
        time.sleep(1)
        # Start gen_ping module.
        self.CANEngine.call_module(2, 's')
        time.sleep(2)
        index = 1
        # Print table of CAN messages sniffed by mod_stat.
        ret = self.CANEngine.call_module(1, 'p')
        print(ret)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        self.assertTrue(len(_bodyList) == 20, "Should be 20 groups of packets")
        self.assertTrue(1790 in _bodyList, "1790 should be there")
        self.assertTrue(1791 in _bodyList, "1791 should be there")
        self.assertTrue(1792 in _bodyList, "1792 should be there")
        self.assertTrue((3, bytes.fromhex("02010d"), "Default", False) in _bodyList[1792], "020902 as packet should be there")
        self.assertTrue((7, bytes.fromhex("062f0307030000"), "Default", False) in _bodyList[1792],
                        "062f0307030000 as packet should be there")
        self.assertTrue((3, bytes.fromhex("020902"), "Default", False) in _bodyList[1792], "020901 as packet should be there")
        self.assertTrue((3, bytes.fromhex("02010d"), "Default", False) in _bodyList[1790], "02010d as packet should be there")
        self.assertFalse((3, bytes.fromhex("020904"), "Default", False) in _bodyList[1791],
                         "020904 as packet should not be there")

        # Print table of CAN messages sniffed by mod_stat.
        ret = self.CANEngine.call_module(1, 'p')
        print(ret)
        # Use gen_replay to replay a range of CAN messages
        self.CANEngine.call_module(0, 'r 0-9')
        time.sleep(2)
        # Print table of CAN messages sniffed by mod_stat.
        ret = self.CANEngine.call_module(1, 'p')
        print(ret)
        _bodyList = self.CANEngine._enabledList[index][1]._bodyList
        # Use gen_stat to analyse the UDS traffic
        ret = self.CANEngine.call_module(1, 'a')
        print(ret)
        self.assertTrue(1 == _bodyList[1800][(
            8,
            bytes.fromhex("1014490201314731"),
            "Default",
            False
        )], "Should be 1 packed replayed")

        self.assertTrue(0 <= ret.find("ASCII: .1G1ZT53826F109149"), "TEXT should be found in response")
        self.assertTrue(0 <= ret.find("Response: 00"), "TEXT should be found in response")
        self.assertTrue(0 <= ret.find("ASCII: I..1G1ZT53826F109149"), "TEXT should be found in response")
        self.assertTrue(0 <= ret.find("DATA: 4902013147315a54353338323646313039313439"), "TEXT should be found in response")
        self.assertTrue(0 <= ret.find("ID: 0x701 Service: 0x2f Sub: 0x3 (Input Output Control By Identifier)"), "Text should be found in response")
        self.assertTrue(0 <= ret.find("ID: 0x6ff Service: 0x1 Sub: 0xd (Req Current Powertrain)"), "Text should be found in response")

    def test_replay_uds_padding(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config('tests/configurations/conf_gen_replay_uds_padding.py')
        self.CANEngine.start_loop()
        time.sleep(1)
        # Start gen_ping module.
        self.CANEngine.call_module(1, 's')
        time.sleep(2)
        # Print table of CAN messages sniffed by mod_stat.
        ret = self.CANEngine.call_module(3, 'p')
        print(ret)
        _bodyList = self.CANEngine._enabledList[3][1]._bodyList
        self.assertTrue(len(_bodyList) == 20, "Should be 20 groups of packets")
        self.assertTrue(1790 in _bodyList, "1790 should be there")
        self.assertTrue(1791 in _bodyList, "1791 should be there")
        self.assertTrue(1792 in _bodyList, "1792 should be there")
        self.assertTrue((8, bytes.fromhex("02010d4141414141"), "USBTin", False) in _bodyList[1792], "020902 as packet should be there")
        self.assertTrue((8, bytes.fromhex("062f030703000041"), "USBTin", False) in _bodyList[1792],
                        "062f0307030000 as packet should be there")
        self.assertTrue((8, bytes.fromhex("0209024141414141"), "USBTin", False) in _bodyList[1792], "020901 as packet should be there")
        self.assertTrue((8, bytes.fromhex("02010d4141414141"), "USBTin", False) in _bodyList[1790], "02010d as packet should be there")
        self.assertFalse((8, bytes.fromhex("0209044141414141"), "USBTin", False) in _bodyList[1791],
                         "020904 as packet should not be there")
        # Replay captured CAN messages with gen_replay
        self.CANEngine.call_module(2, 'r')
        time.sleep(2)
        # Print table of CAN messages sniffed by mod_stat.
        ret = self.CANEngine.call_module(3, 'p')
        print(ret)
        _bodyList = self.CANEngine._enabledList[3][1]._bodyList
        # Use gen_stat to analyse the UDS traffic
        ret = self.CANEngine.call_module(3, 'a')
        print(ret)
        self.assertTrue(1 == _bodyList[1800][(
            8,
            bytes.fromhex("1014490201314731"),
            "USBTin",
            False
        )], "Should be 1 packed replayed")

        self.assertTrue(0 <= ret.find("ASCII: .1G1ZT53826F109149"), "TEXT should be found in response")
        self.assertTrue(0 <= ret.find("Response: 00"), "TEXT should be found in response")
        self.assertTrue(0 <= ret.find("ASCII: I..1G1ZT53826F109149"), "TEXT should be found in response")
        self.assertTrue(0 <= ret.find("DATA: 4902013147315a54353338323646313039313439"), "TEXT should be found in response")
        self.assertTrue(0 <= ret.find("ID: 0x701 Service: 0x2f Sub: 0x3 (Input Output Control By Identifier)"), "Text should be found in response")
        self.assertTrue(0 <= ret.find("ID: 0x6ff Service: 0x1 Sub: 0xd (Req Current Powertrain)"), "Text should be found in response")

    def test_replay_timestamp(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config('tests/configurations/conf_gen_replay_timestamp.py')
        self.CANEngine.start_loop()
        time.sleep(1)
        # Get number of loaded CAN packets from gen_replay.
        num = self.CANEngine.call_module(0, 'p')
        self.assertTrue(0 <= num.find("Loaded packets: 11"), "Should be 11 packets")
        time1 = time.clock()
        # Replay loaded CAN packets with gen_replay.
        self.CANEngine.call_module(0, 'r')
        while self.CANEngine._enabledList[0][1]._status < 100.0:
            continue
        # Print table of CAN messages sniffed by mod_stat.
        ret = self.CANEngine.call_module(1, 'p')
        print(ret)
        time2 = time.clock()
        print("TIME: " + str(time2 - time1))
        # Get current status of mod_stat
        st = self.CANEngine.call_module(1, 'S')
        print(st)
        self.assertTrue(0 <= st.find("Sniffed frames (overall): 11"), "Should be 11 packets")
        # Dump CAN packets sniffed by mod_stat to file.
        self.CANEngine.call_module(1, 'r tests/data/format.dump')
        self.assertTrue(13.99 < time2 - time1 < 15.99, "Should be around 14 seconds")

    def test_replay_timestamp2(self):
        self.CANEngine = CANSploit()
        self.CANEngine.load_config('tests/configurations/conf_gen_replay_timestamp2.py')
        self.CANEngine.start_loop()
        time.sleep(1)
        # Get number of loaded CAN packets from gen_replay.
        num = self.CANEngine.call_module(0, 'p')
        self.assertTrue(0 <= num.find("Loaded packets: 11"), "Should be 11 packets")
        time1 = time.clock()
        # Replay loaded CAN packets with gen_replay.
        self.CANEngine.call_module(0, 'r')
        while self.CANEngine._enabledList[0][1]._status < 100.0:
            continue
        # Print table of CAN messages sniffed by mod_stat.
        ret = self.CANEngine.call_module(1, 'p')
        print(ret)
        time2 = time.clock()
        print("TIME: " + str(time2 - time1))
        self.assertTrue(13.99 < time2 - time1 < 15.99, "Should be around 14 seconds")
        # Get current status of mod_stat
        st = self.CANEngine.call_module(1, 'S')
        self.assertTrue(0 <= st.find("Sniffed frames (overall): 11"), "Should be 11 packets")