'''
This module starts the webcam of the user. The user can then press 'p' to get
predictions regarding the fruit he's holding in the frame or 'Space' to save
the current frame locally. The key 'q' closes the window.
'''
import logging
from datetime import datetime
import argparse
from pathlib import Path
import cv2
from predict import predict

def get_args():
    '''
    Arguments for CLI.
    '''
    parser = argparse.ArgumentParser(
        description='''
            takes pictures from the webcam. use <q> to end the session 
            and <spacebar> to capture an image.
        '''
    )
    parser.add_argument("name", help="folder name to store images", nargs='?', default='out')
    return parser.parse_args()

def key_action():
    '''
    Defines keys like here: https://www.ascii-code.com/
    '''
    k = cv2.waitKey(10)
    if k == 113: # q button
        return 'q'
    if k == 32: # space bar
        return 'space'
    if k == 112: # p button
        return "p"
    return None

def write_image(folder, frame):
    '''
    Saves frames as an image.
    '''
    time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    out = f'{folder}/{time}.png'
    cv2.imwrite(out, frame)
    logging.info(f'written {out}')

def init_cam():
    '''
    Initializes webcam.
    '''
    logging.info('start web cam')
    cap = cv2.VideoCapture(0)

    # Check success
    if not cap.isOpened():
        raise Exception("Could not open video device")

    # Set properties. Each returns === True on success (i.e. correct resolution)
    assert cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    assert cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    return cap

def add_text(ft, text, frame):
    '''
    Put some rectangular box on the image
    '''
    frame[-70:, :, : ] = (191, 191, 191)
    ft.putText(frame, text,
               org=(30, 445),
               color=(0, 0, 0),
               fontHeight=30,
               line_type=cv2.LINE_AA,
               bottomLeftOrigin=True,
               thickness=-1)

if __name__ == "__main__":

    logging.getLogger().setLevel(logging.INFO)

    ft = cv2.freetype.createFreeType2()
    ft.loadFontData(fontFileName="../fonts/OpenSansEmoji.ttf",
                    id=0)

    args = get_args()

    logging.info('create folder if not exists')
    Path(args.name).mkdir(parents=True, exist_ok=True)

    cap = init_cam()

    key = None
    pred_made = False

    try:
        while key != 'q':
            # Capture frame-by-frame
            ret, frame = cap.read()

            # fliping the image
            frame = cv2.flip(frame, 1)

            key = key_action()

            if key == 'space':
                # space key was pressed, write the image without overlay
                write_image(args.name, frame)

            if key == "p":
                pred_made = True
                last_prediction = datetime.now()
                frame_now = frame

            if key is None:
                # no key was pressed, display the overlay
                time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
            #    add_text(time, frame)
                if pred_made:
                    result = predict(frame_now)
                    if (datetime.now() - last_prediction).total_seconds() < 2:
                        add_text(ft, result, frame)
                    else:
                        pred_made = False

            # Display the resulting frame
            cv2.imshow('frame', frame)

    finally:
        # when everything done, release the capture
        logging.info('quit webcam')
        cap.release()
        cv2.destroyAllWindows()
