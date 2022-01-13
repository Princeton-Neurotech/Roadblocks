import time
import numpy as np
import pandas as pd
import statistics

import brain_data_test 

import brainflow
from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels
from brainflow.data_filter import DataFilter, FilterTypes, AggOperations


class braindata:

    def __init__(self, boardID=-1, serial=''):
        self.isRunning = False
        self.myBoardID = boardID
        BoardShim.enable_dev_board_logger()
        self.params = BrainFlowInputParams()
        self.params.serial_port = serial
        self.board = BoardShim(self.myBoardID, self.params)
        self.total_brain_data = None
        self.brain_training_features = None
        self.mean = None

    def startStream(self):
        """
        Tells the bord to being streaming data
        """
        BoardShim.enable_dev_board_logger()
        self.board.prepare_session()
        # initiate stream
        self.board.start_stream(45000, '')
        self.isRunning = True
        self.board.log_message(LogLevels.LEVEL_INFO, "Start sleeping in the main thread")
        # time.sleep(sleepTime)  # sleep 30 seconds
        # get the data
        self.data = self.board.get_board_data()

    def getData(self):
        """
        Gets the data from the board (presumably all of it since stream
        was started
        :return: The data from the board
        """
        return self.board.get_board_data()

    def getCurrentData(self, num_samples: int):
        """
        Gets the current (updated) data from the board
        :param num_samples: The amount of samples the returned ndarray will hold
        :return: The current board data
        """
        return self.board.get_current_board_data(num_samples)

    def get_samplingRate(self):
        """
        Get the rate at which the board samples data
        (i.e.: The muse has an SR of about 256 Hz
        :return: The sampling rate of a certain board
        """
        return self.board.get_sampling_rate(self.myBoardID)

    def getEEGChannels(self):
        """
        Gets the EEG channels from the board being used
        :return: The amt of channels for streaming EEG on the board
        """
        return self.board.get_eeg_channels(self.myBoardID)

    def stopStream(self):
        """
        Tells the board to stop streaming data
        """
        if self.isRunning:
            print('Stopping Stream')
            self.board.stop_stream()
            self.board.release_session()
        else:
            print("BOARD WAS NEVER STARTED")

    def run(self, streamTime: int):
        """
        Tells the board to run a specific test for a specific amt of time
        [FOR DEBUGGING]
        :param streamTime: The time the board will be streaming
        """
        BoardShim.enable_dev_board_logger()
        params = BrainFlowInputParams()

        # BOARD IDs internally in brainflow
        SYNTH_BOARD = int(-1)
        CYTON = int(0)
        MUSE2 = int(22)

        myCytonSerialPort = 'COM3'
        noSerial = ''

        params.serial_port = noSerial

        # create our board
        # board = BoardShim(SYNTH_BOARD, params)
        board = BoardShim(self.myBoardID, params)
        board.prepare_session()

        # initiate stream
        board.start_stream(45000, '')
        board.log_message(LogLevels.LEVEL_INFO, "Start sleeping in the main thread")
        time.sleep(streamTime)  # sleep 30 seconds

        # get the data
        self.data = board.get_board_data()

        # board.stop_stream()
        # board.release_session()

        print(self.data)  # for now print the data we can write it to a file

    def getBoard(self):
        """
        Lets us know what board we are using
        :return: The id of the board being used
        """
        if self.myBoardID == -1:
            print("Default Board is being used: SYNTHETIC")
        elif self.myBoardID == 0:
            print("OpenBCI Cyton is being used: CYTON")
        elif self.myBoardID == 22:
            print("Interaxon Muse 2 with bluetooth dongle is being used: MUSE2")
        elif self.myBoardID == 38:
            print("Interaxon Muse 2 without bluetooth dongle is being used: MUSE2")
        return self.myBoardID

    def setBoard(self, boardID: int):
        """
        Change the ID of the Board we are using
        :param boardID: -1 for Synth, 0 for Cyton, 22 for MUSE2
        """
        self.myBoardID = boardID

    def collectData(self):
        """
            Collect data, taking mean, every 5s, organize a sliding window queue in which the window 
            length is 10s and there is an overlap of 2 ie. 0-10, 5-15, 10-20 etc. for every 300s (5 min). 
        """
                    
        start_time = time.time()
        created_df = False

        while True:
            self.total_brain_data = brain_data_test.calc_feature_vector(myBoard.getCurrentData(250))
            # feature_list = training_features[-1].copy()
            # print(len(brain_fv[0]),len(brain_fv[-1]))
            # print(str(str(counter1) + '_' + str(round(time.time()-start_time,2))) * 1000)

            # first 3s lengths of lists change (unknown why) but afterwards doesn't change
            # if (time.time() - start_time) > 3: 
            if created_df is False:
                self.brain_training_features = pd.DataFrame(columns=self.total_brain_data[-1])
                created_df = True

            self.brain_training_features.loc[len(self.brain_training_features)] = self.total_brain_data[0] 
            # print(self.brain_training_features)
            
            for col in self.brain_training_features:
                self.brain_training_features[col] = self.brain_training_features[col].astype(float)
                self.brain_training_features['5rSUMMARY ' + col] = self.brain_training_features[col].rolling(5).mean() 

            time.sleep(1)
    
        """
        def repeatCollectData(self):
            start_time = time.time()
            interval = 1
            for i in range(20):
                time.sleep(start_time + i*interval - time.time())
                collectData()
        """

if __name__ == "__main__":
    myBoard = braindata(-1, 'COM3')
    # print(brainflow.__version__)
    myBoard.startStream()
    sampling_rate = myBoard.get_samplingRate()
    eeg_channels = myBoard.getEEGChannels()
    collect_data = myBoard.collectData()
    # repeat_collect_data = myBoard.repeatCollectData()
    # myBoard.stopStream()