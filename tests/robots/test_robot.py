import os

import compas
import pytest
from compas.geometry import Frame
from compas.robots import RobotModel

from compas.robots.base_artist import BaseRobotModelArtist

from compas_fab.robots import Robot
from compas_fab.robots import RobotSemantics
from compas_fab.robots.ur5 import Robot as Ur5Robot

BASE_FOLDER = os.path.dirname(__file__)


@pytest.fixture
def panda_srdf():
    return os.path.join(BASE_FOLDER, 'fixtures', 'panda_semantics.srdf')


@pytest.fixture
def panda_urdf():
    return os.path.join(BASE_FOLDER, 'fixtures', 'panda.urdf')


@pytest.fixture
def panda_robot_instance(panda_urdf, panda_srdf):
    model = RobotModel.from_urdf_file(panda_urdf)
    semantics = RobotSemantics.from_srdf_file(panda_srdf, model)
    return Robot(model, semantics=semantics)


@pytest.fixture
def ur5_robot_instance():
    return Ur5Robot()


@pytest.fixture
def ur5_joints(ur5_robot_instance):
    return ur5_robot_instance.model.joints


@pytest.fixture
def ur5_links(ur5_robot_instance):
    return ur5_robot_instance.model.links


def test_basic_name_only():
    robot = Robot.basic('testbot')
    assert robot.artist is None


def test_basic_name_joints_links(ur5_joints, ur5_links):
    robot = Robot.basic('testbot', joints=ur5_joints, links=ur5_links)
    assert len(robot.model.links) == 11
    assert len(robot.get_configurable_joint_names()) == 6


def test_basic_name_joints(ur5_joints):
    robot = Robot.basic('testbot', joints=ur5_joints)
    assert len(robot.model.joints) == 10


def test_basic_name_links(ur5_links):
    robot = Robot.basic('testbot', links=ur5_links)
    assert len(robot.model.links) == 11


def test_basic_attr():
    robot = Robot.basic('testbot', location='rfl')
    assert robot.model.attr['location'] == 'rfl'


def test_name(panda_robot_instance):
    robot = panda_robot_instance
    assert robot.name == 'panda'


def test_group_names(ur5_robot_instance):
    robot = ur5_robot_instance
    assert robot.group_names == ['manipulator', 'endeffector']


def test_main_group_name(panda_robot_instance):
    robot = panda_robot_instance
    assert robot.main_group_name == 'panda_arm_hand'


def test_root_name(ur5_robot_instance):
    robot = ur5_robot_instance
    assert robot.root_name == 'world'


def test_get_end_effector_link_name(panda_robot_instance):
    robot = panda_robot_instance
    assert robot.get_end_effector_link_name(group=None) == 'panda_rightfinger'
    assert robot.get_end_effector_link_name(group='panda_arm_hand') == 'panda_rightfinger'
    assert robot.get_end_effector_link_name(group='panda_arm') == 'panda_link8'


def test_get_end_effector_link_name_wrong_group(panda_robot_instance):
    robot = panda_robot_instance
    with pytest.raises(KeyError):
        robot.get_end_effector_link_name(group='panda_leg')


@pytest.mark.parametrize('group', [None, 'endeffector'])
def test_get_end_effector_link(ur5_robot_instance, group):
    robot = ur5_robot_instance
    assert isinstance(robot.get_end_effector_link(group=group), compas.robots.Link)


def test_get_end_effector_frame(panda_robot_instance):
    robot = panda_robot_instance
    assert round(robot.get_end_effector_frame(group=None).point.x, 3) == .301
    assert round(robot.get_end_effector_frame(group='panda_arm').point.x, 3) == .359


@pytest.mark.parametrize('group, remove_semantics, expected_result',
                         [(None,          False, 'base_link'),
                          (None,          True,  'base_link'),
                          ('endeffector', False, 'ee_link'),
                          ('endeffector', True,  'base_link')])
def test_get_base_link_name(ur5_robot_instance, group, remove_semantics, expected_result):
    robot = ur5_robot_instance
    if remove_semantics:
        robot.semantics = None
    assert robot.get_base_link_name(group=group) == expected_result


@pytest.mark.parametrize('group', [None, 'panda_arm'])
def test_get_base_link(panda_robot_instance, group):
    robot = panda_robot_instance
    link = robot.get_base_link(group=group)
    assert len(link.joints) == 1


@pytest.mark.parametrize('group', [None, 'panda_arm'])
@pytest.mark.parametrize('add_artist', [True, False])
def test_get_base_frame(panda_robot_instance, group, add_artist):
    robot = panda_robot_instance
    if add_artist:
        robot.artist = BaseRobotModelArtist(robot.model)
    assert robot.get_base_frame(group=group) == Frame.worldXY()


def test_get_base_frame_when_link_has_parent(ur5_robot_instance):
    robot = ur5_robot_instance
    assert robot.get_base_frame(group='endeffector')


@ pytest.mark.parametrize('group', ['endeffector', 'manipulator', None])
@ pytest.mark.parametrize('remove_semantics', [False, True])
def test_get_configurable_joints(ur5_robot_instance, group, remove_semantics):
    # TODO: Test duplicate joints
    robot = ur5_robot_instance
    if remove_semantics:
        robot.semantics = None
    assert len(robot.get_configurable_joints()) == 6
