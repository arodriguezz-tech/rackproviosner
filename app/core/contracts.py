from . import event_names as e
CONTRACTS={
e.SERIAL_CONNECTED:{'ok','port','baud'}, e.SERIAL_COMMAND_FINISHED:{'name','output'},
e.DISCOVERY_COMPLETED:{'result'}, e.LLDP_COMPLETED:{'neighbors','raw_output'},
e.INVENTORY_SAVED:{'rack_serial'}, e.INVENTORY_VERIFIED:{'state','role','reason','rack_serial'},
e.SKU_REVISION_SAVED:{'sku','version','revision_type','changes'}, e.SETTINGS_CHANGED:set(),
e.READINESS_EVALUATED:{'result'}}
