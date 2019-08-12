#!/usr/bin/env python
# -*- coding: utf-8 -*-
from learnbot_dsl.Clients.Client import *
from learnbot_dsl.functions import getFuntions
import os, numpy as np, PIL.Image as Image, PIL.ImageFilter as ImageFilter, io, cv2, paho.mqtt.client, threading, math
import cozmo as cozmoR
from cozmo.util import radians, degrees, distance_mm, speed_mmps
from learnbot_dsl.Clients.Devices import *

cozmo = None
K = 2  # Speed constant
L = 45  # Distance between wheels


def cozmo_program(_robot: cozmoR.robot.Robot):
    global cozmo
    global stopThread
    cozmo = _robot
    while not stopThread:
        pass

class Robot(Client):
    devicesAvailables = ["base", "camera", "display", "jointmotor", "acelerometer", "gyroscope", "speaker"]

    def __init__(self):
        global cozmo
        global stopThread
        stopThread = False
        Client.__init__(self)
        self.distanceSensors = DistanceSensors(_readFunction=self.deviceReadLaser)
        self.acelerometer = Acelerometer(_readFunction=self.deviceReadAcelerometer)
        self.gyroscope = Gyroscope(_readFunction=self.deviceReadGyroscope)
        self.camera = Camera(_readFunction=self.deviceReadCamera)
        self.base = Base(_callFunction=self.deviceMove)
        self.display = Display(_setEmotion=self.deviceSendEmotion, _setImage=None)
        self.addJointMotor("CAMERA", _JointMotor=JointMotor(_callDevice=self.deviceSendAngleHead, _readDevice=None))
        self.addJointMotor("ARM", _JointMotor=JointMotor(_callDevice=self.deviceSendAngleArm, _readDevice=None))
        self.speaker = Speaker(_sendText=self.deviceSendText)
        self.connectToRobot()
        self.cozmo = cozmo
        self.cozmo.camera.image_stream_enabled = True
        self.cozmo.camera.color_image_enabled = True
        self.start()

    def connectToRobot(self):
        cozmoR.robot.Robot.drive_off_charger_on_connect = False
        self.t = threading.Thread(target=lambda: cozmoR.run_program(cozmo_program))
        self.t.start()
        time.sleep(2)

    def disconnect(self):
        print("disconnecting")
        self.deviceMove(0,0)
        self.cozmo.wait_for_all_actions_completed()
        global stopThread
        stopThread = True

    def deviceSendText(self, text):
        self.cozmo.say_text(text=text, in_parallel=True)

    def deviceSendAngleArm(self, _angle):
        if _angle > 0.79:
            _angle = 0.79
        elif _angle < -0.20:
            _angle = -0.20
        a = (_angle + 0.20) / (0.79 + 0.20)
        self.cozmo.set_lift_height(a, in_parallel=True)

    def deviceSendAngleHead(self, _angle):
        a = radians(_angle)
        self.cozmo.set_head_angle(a, in_parallel=True)

    def deviceSendEmotion(self, _emotion):
        if self.cozmo.has_in_progress_actions:
            return
        trigger = None
        if _emotion is Emotions.Joy:
            trigger = cozmoR.anim.Triggers.PeekABooGetOutHappy
        elif _emotion is Emotions.Sadness:
            trigger = cozmoR.anim.Triggers.PeekABooGetOutSad
        elif _emotion is Emotions.Surprise:
            trigger = cozmoR.anim.Triggers.PeekABooSurprised
        elif _emotion is Emotions.Disgust:
            trigger = None
        elif _emotion is Emotions.Anger:
            trigger = cozmoR.anim.Triggers.DriveEndAngry
        elif _emotion is Emotions.Fear:
            trigger = cozmoR.anim.Triggers.CodeLabScaredCozmo
        elif _emotion is Emotions.Neutral:
            trigger = cozmoR.anim.Triggers.NeutralFace
        if trigger is not None:
            self.cozmo.play_anim_trigger(trigger, in_parallel=True, ignore_body_track=True,
                                         ignore_head_track=True, ignore_lift_track=True)

    def deviceReadGyroscope(self):
        return self.cozmo.gyro.x_y_z

    def deviceReadAcelerometer(self):
        return self.cozmo.accelerometer.x_y_z

    def deviceReadLaser(self):
        return {"bottom": [self.cozmo.is_cliff_detected]}

    def deviceReadCamera(self):
        lastimg = self.cozmo.world.latest_image
        if lastimg is not None:
            img = lastimg.annotate_image()
            open_cv_image = np.array(img.convert('RGB'))
            cv_image = open_cv_image[:, :, ::-1].copy()
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
            return cv_image, True
        else:
            print("error leyendo camara")
            return None, False

    def deviceMove(self, SAdv, SRot):
        if SRot != 0.:
            print(SRot)
            Rrot = SAdv / math.tan(SRot)

            Rl = Rrot - (L / 2)
            l_wheel_speed = SRot * Rl * K

            Rr = Rrot + (L / 2)
            r_wheel_speed = SRot * Rr * K
        else:
            l_wheel_speed = SAdv * K
            r_wheel_speed = SAdv * K
        self.cozmo.drive_wheel_motors(r_wheel_speed, l_wheel_speed, 0, 0)


if __name__ == '__main__':
    ebo = Robot()
    ebo.speakText("hola")
    ebo.join()
