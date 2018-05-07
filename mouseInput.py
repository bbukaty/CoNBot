import pythoncom, pyHook 
 
def OnMouseEvent(event):
  # called when mouse events are received
  print('MessageName:',event.MessageName)
  print('Message:',event.Message)
  print('Time:',event.Time)
  print('Window:',event.Window)
  print('WindowName:',event.WindowName)
  print('Position:',event.Position)
  print('Wheel:',event.Wheel)
  print('Injected:',event.Injected)
  print('---')
  
  # return True to pass the event to other handlers
  return True
 
# create a hook manager
hm = pyHook.HookManager()
# watch for all mouse events
hm.MouseAll = OnMouseEvent
# set the hook
hm.HookMouse()
# wait forever
pythoncom.PumpMessages()