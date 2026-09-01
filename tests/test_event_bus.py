from app.core.events import EventBus

def test_specific_and_wildcard_subscribers_receive_event():
    bus=EventBus(); specific=[]; wildcard=[]
    bus.subscribe("inventory.saved",lambda e:specific.append(e.payload))
    bus.subscribe("*",lambda e:wildcard.append(e.name))
    bus.publish("inventory.saved",rack_serial="R1")
    assert specific == [{"rack_serial":"R1"}]
    assert wildcard == ["inventory.saved"]
