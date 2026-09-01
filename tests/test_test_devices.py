from app.domain.models import DeviceIdentity
TEST_DEVICES=[DeviceIdentity('NK001','001122334451','Nokia 7215 IXS','MX'),DeviceIdentity('MLX001','001122334452','SN4700','NS1'),DeviceIdentity('MLX002','001122334453','SN4700','NS2'),DeviceIdentity('OLD001','001122334454','SN2700',None),DeviceIdentity('AR001','001122334455','Arista H20',None)]
def test_device_fixture_matrix():
 assert len(TEST_DEVICES)==5; assert {d.model for d in TEST_DEVICES}=={'Nokia 7215 IXS','SN4700','SN2700','Arista H20'}; assert len({d.serial for d in TEST_DEVICES})==5; assert len({d.mac for d in TEST_DEVICES})==5
