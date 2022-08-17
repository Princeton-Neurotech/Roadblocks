import keyboard_features
import pandas as pd
import time
import roadblock_ml

# keyboard functions
def worker1(namespace):
    print("starting keyboard data collection")
    keyboard1 = keyboard_features.keyboard()
    while True:
        namespace.keyboard = keyboard1.realtime(keyboard1.text) 
        print(namespace.keyboard)
 
 # brain data functions
def worker2(board, namespace):
    print("starting brain data collection")
    # myBoard = brain_data_collection.braindata(38, '/dev/cu.usbserial-DM03H3ZF')
    try:
        board.startStream()
    except:
        print("Stream not started")
         
    for i in range(10):
        board.collectData(board)        
        namespace.brain = board.define_global_muse_data()
        # print(namespace.brain)
    
# web interface functions
def worker3(mySelenium, myUID):
    while True:
        print("process 2")
        mySelenium.processSelenium(myUID)
        time.sleep(5)
        pd.options.display.max_columns = None
        keyboard1 = keyboard_features.keyboard()
        prediction = roadblock_ml.rb_ml()
        # print(keyboard1.keyboard_training_features)

def worker4():
    tm = 5400 # 5400, 9000
    while(tm <= 5400):
        mint = tm / 60
        hrs = mint/60
        sec = tm % 60
        print("time left --> {}:{}:{}".format(hrs,mint,sec))
        tm+=1
        time.sleep(1)