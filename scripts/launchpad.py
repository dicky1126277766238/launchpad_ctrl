import pygame.midi
import rospy
from launchpad_ctrl.msg import LaunchpadKey


def findDevices():
  pygame.midi.init()
  n_devices = pygame.midi.get_count()
  keyword = "MK2"
  ret = {'input': -1, 'output': -1}

  for d in range(n_devices):
    di = pygame.midi.get_device_info(d)
    print("Device %d: %s" % (d, str(di)))
    if di[1].find(keyword) != -1 and di[2] == 1:
      # Input side
      print("Found target input device")
      ret['input'] = d
    elif di[1].find(keyword) != -1 and di[3] == 1:
      # Output side
      print("Found target output device")
      ret['output'] = d
  print(ret)
  # pygame.midi.quit()
  return ret


class Launchpad:
  def __init__(self):
    self.connect()

  # pygame.midi.init()

  def connect(self):
    ret = findDevices()
    self.in_id = ret['input']
    self.out_id = ret['output']
    self.midi_input = pygame.midi.Input(self.in_id)
    self.midi_output = pygame.midi.Output(self.out_id)
    self.ledOff()
    # flush
    rospy.sleep(0.1)
    while (self.midi_input.poll()):
      self.midi_input.read(1)

  def disconnect(self):
    self.ledOff()
    self.midi_input.close()
    self.midi_output.close()
    pygame.midi.quit()

  def ledOff(self):
    self.midi_output.write_sys_ex(0, [0xf0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x0e, 0x00, 0xf7])

  def scrollText(self, color, loop, text):
    msg = [0xf0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x14]
    msg = msg + [color, loop] + [ord(c) for c in text] + [0xf7]
    self.midi_output.write_sys_ex(0, msg)

  def lightOne(self, led_num, c):
    self.midi_output.write_sys_ex(0, [0xf0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x0a, led_num, c, 0xf7])

  def lightMulti(self, m):
    m_output = []
    for x, y, c in m:
      m_output += [xyToKey(x,y)]
      m_output += [c]
    self.midi_output.write_sys_ex(0, [0xf0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x0a] + m_output + [0xf7])

  def lightColumn(self, col_num, c):
    self.midi_output.write_sys_ex(0, [0xf0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x0c, col_num, c, 0xf7])

  def lightRow(self, row_num, c):
    self.midi_output.write_sys_ex(0, [0xf0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x0d, row_num, c, 0xf7])

  def lightAll(self, row_num, c):
    self.midi_output.write_sys_ex(0, [0xf0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x0e, c, 0xf7])

  def lightOneRGB(self, led_num, r, g, b):  # maximum color value is 63 0x3f
    self.midi_output.write_sys_ex(0, [0xf0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x0b, led_num, r, g, b, 0xf7])

  def lightMultiRGB(self, m):
    m_output = []
    counter = 0
    for i,(x, y, r, g, b) in enumerate(m):
      m_output += [xyToKey(x,y)]
      m_output += [r, g, b]
      counter += 1
      if counter == 15:
        self.midi_output.write_sys_ex(0, [0xf0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x0b] + m_output + [0xf7])
        m_output = []
        counter = 0
    self.midi_output.write_sys_ex(0, [0xf0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x0b] + m_output + [0xf7])

  def flash(self, led_num, c):
    self.midi_output.write_sys_ex(0, [0xf0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x23, 0x00, led_num, c, 0xf7])

  def presetMode(self, num):
    self.midi_output.write_sys_ex(0, [0xf0, 0x00, 0x20, 0x29, 0x02, 0x18, 0x22, num, 0xf7])


def parseKeyEvent(keyNum, keydown):
  event = LaunchpadKey()
  event.type = 'square'
  if (keydown == 0):
    event.keydown = False
  else:
    event.keydown = True
  if (keyNum >= 104):
    event.y = keyNum - 104
    event.x = 8
    event.type = {
      104: 'UP',
      105: 'DOWN',
      106: 'LEFT',
      107: 'RIGHT',
      108: 'SESSION',
      109: 'USER_1',
      110: 'USER_2',
      111: 'MIXER'
    }[keyNum]
  else:
    event.x = keyNum / 10 - 1
    event.y = keyNum % 10 - 1
  if (event.y == 8):
    event.type = {
      0: 'RECORD_ARM',
      1: 'SOLO',
      2: 'MUTE',
      3: 'STOP',
      4: 'SEND_B',
      5: 'SEND_A',
      6: 'PAN',
      7: 'VOLUME'
    }[event.x]
  return event


def xyToKey(x, y):
  if (x == 8):
    return y + 104
  else:
    return ((x + 1) * 10) + (y + 1)
