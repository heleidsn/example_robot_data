import sys
from os.path import dirname, exists, join

import numpy as np
import pinocchio as pin
from pinocchio.robot_wrapper import RobotWrapper

try:
    from .path import EXAMPLE_ROBOT_DATA_MODEL_DIR, EXAMPLE_ROBOT_DATA_SOURCE_DIR
except ImportError:
    pass


def getModelPath(subpath, verbose=False):
    source = dirname(dirname(dirname(__file__)))  # top level source directory
    paths = [
        # function called from "make release" in build/ dir
        join(dirname(dirname(dirname(source))), "robots"),
        # function called from a build/ dir inside top level source
        join(dirname(source), "robots"),
        # function called from top level source dir
        join(source, "robots"),
    ]
    try:
        EXAMPLE_ROBOT_DATA_MODEL_DIR

        # function called from installed project
        paths.append(EXAMPLE_ROBOT_DATA_MODEL_DIR)
        # function called from off-tree build dir
        paths.append(EXAMPLE_ROBOT_DATA_SOURCE_DIR)
    except NameError:
        pass
    paths += [join(p, "../../../share/example-robot-data/robots") for p in sys.path]
    for path in paths:
        if exists(join(path, subpath.strip("/"))):
            if verbose:
                print("using %s as modelPath" % path)
            return path
    raise IOError("%s not found" % subpath)


def readParamsFromSrdf(
    model,
    SRDF_PATH,
    verbose=False,
    has_rotor_parameters=True,
    referencePose="half_sitting",
):
    if has_rotor_parameters:
        pin.loadRotorParameters(model, SRDF_PATH, verbose)
    model.armature = np.multiply(
        model.rotorInertia.flat, np.square(model.rotorGearRatio.flat)
    )
    pin.loadReferenceConfigurations(model, SRDF_PATH, verbose)
    q0 = pin.neutral(model)
    if referencePose is not None:
        q0 = model.referenceConfigurations[referencePose].copy()
    q0 = pin.normalize(model, q0)
    return q0


class RobotLoader(object):
    path = ""
    urdf_filename = ""
    srdf_filename = ""
    sdf_filename = ""
    sdf_root_link_name = ""
    sdf_parent_guidance = []
    urdf_subpath = "robots"
    srdf_subpath = "srdf"
    sdf_subpath = ""
    ref_posture = "half_sitting"
    has_rotor_parameters = False
    free_flyer = False
    model_path = None

    def __init__(self, verbose=False):
        self.verbose = verbose
        if self.urdf_filename:
            if self.sdf_filename:
                raise AttributeError("Please choose between URDF *or* SDF")
            df_path = join(self.path, self.urdf_subpath, self.urdf_filename)
            builder = RobotWrapper.BuildFromURDF
            if self.model_path is None:
                self.model_path = getModelPath(df_path, self.verbose)
            self.df_path = join(self.model_path, df_path)
            self.robot = builder(
                self.df_path,
                [join(self.model_path, "../..")],
                pin.JointModelFreeFlyer() if self.free_flyer else None,
            )
        else:
            df_path = join(self.path, self.sdf_subpath, self.sdf_filename)
            try:
                builder = RobotWrapper.BuildFromSDF
                if self.model_path is None:
                    self.model_path = getModelPath(df_path, self.verbose)
                self.df_path = join(self.model_path, df_path)
                if tuple(int(i) for i in pin.__version__.split(".")) > (2, 9, 1):
                    self.robot = builder(
                        self.df_path,
                        package_dirs=[join(self.model_path, "../..")],
                        root_joint=(
                            pin.JointModelFreeFlyer() if self.free_flyer else None
                        ),
                        root_link_name=self.sdf_root_link_name,
                        parent_guidance=self.sdf_parent_guidance,
                    )
                else:
                    self.robot = builder(
                        self.df_path,
                        package_dirs=[join(self.model_path, "../..")],
                        root_joint=(
                            pin.JointModelFreeFlyer() if self.free_flyer else None
                        ),
                    )
            except AttributeError:
                raise ImportError("Building SDF models require pinocchio >= 3.0.0")

        if self.srdf_filename:
            self.srdf_path = join(
                self.model_path, self.path, self.srdf_subpath, self.srdf_filename
            )
            self.robot.q0 = readParamsFromSrdf(
                self.robot.model,
                self.srdf_path,
                self.verbose,
                self.has_rotor_parameters,
                self.ref_posture,
            )

            if pin.WITH_HPP_FCL and pin.WITH_HPP_FCL_BINDINGS:
                # Add all collision pairs
                self.robot.collision_model.addAllCollisionPairs()

                # Remove collision pairs per SRDF
                pin.removeCollisionPairs(
                    self.robot.model, self.robot.collision_model, self.srdf_path, False
                )

                # Recreate collision data since the collision pairs changed
                self.robot.collision_data = self.robot.collision_model.createData()
        else:
            self.srdf_path = None
            self.robot.q0 = pin.neutral(self.robot.model)
        root = getModelPath(self.path)
        self.robot.urdf = join(root, self.path, self.urdf_subpath, self.urdf_filename)

        if self.free_flyer:
            self.addFreeFlyerJointLimits()

    def addFreeFlyerJointLimits(self):
        ub = self.robot.model.upperPositionLimit
        ub[:7] = 1
        self.robot.model.upperPositionLimit = ub
        lb = self.robot.model.lowerPositionLimit
        lb[:7] = -1
        self.robot.model.lowerPositionLimit = lb


class B1Loader(RobotLoader):
    path = "b1_description"
    urdf_filename = "b1.urdf"
    urdf_subpath = "urdf"
    srdf_filename = "b1.srdf"
    ref_posture = "standing"
    free_flyer = True


class Go1Loader(RobotLoader):
    path = "go1_description"
    urdf_filename = "go1.urdf"
    urdf_subpath = "urdf"
    srdf_filename = "go1.srdf"
    ref_posture = "standing"
    free_flyer = True


class A1Loader(RobotLoader):
    path = "a1_description"
    urdf_filename = "a1.urdf"
    urdf_subpath = "urdf"
    srdf_filename = "a1.srdf"
    ref_posture = "standing"
    free_flyer = True


class Z1Loader(RobotLoader):
    path = "z1_description"
    urdf_filename = "z1.urdf"
    urdf_subpath = "urdf"
    srdf_filename = "z1.srdf"
    ref_posture = "arm_up"


class B1Z1Loader(B1Loader):
    urdf_filename = "b1-z1.urdf"
    srdf_filename = "b1-z1.srdf"
    ref_posture = "standing_with_arm_home"


class ANYmalLoader(RobotLoader):
    path = "anymal_b_simple_description"
    urdf_filename = "anymal.urdf"
    srdf_filename = "anymal.srdf"
    ref_posture = "standing"
    free_flyer = True


class ANYmalCLoader(RobotLoader):
    path = "anymal_c_simple_description"
    urdf_subpath = "urdf"
    urdf_filename = "anymal.urdf"
    srdf_filename = "anymal.srdf"
    ref_posture = "standing"
    free_flyer = True


class LaikagoLoader(RobotLoader):
    path = "laikago_description"
    urdf_subpath = "urdf"
    urdf_filename = "laikago.urdf"
    free_flyer = True


class ANYmalKinovaLoader(ANYmalLoader):
    urdf_filename = "anymal-kinova.urdf"
    srdf_filename = "anymal-kinova.srdf"
    ref_posture = "standing_with_arm_up"


class BaxterLoader(RobotLoader):
    path = "baxter_description"
    urdf_filename = "baxter.urdf"
    urdf_subpath = "urdf"


class CassieLoader(RobotLoader):
    path = "cassie_description"
    if tuple(int(i) for i in pin.__version__.split(".")) > (2, 9, 1):
        sdf_filename = "cassie.sdf"
    else:
        sdf_filename = "cassie_v2.sdf"
    sdf_subpath = "robots"
    srdf_filename = "cassie_v2.srdf"
    ref_posture = "standing"
    free_flyer = True
    sdf_root_link_name = "pelvis"
    sdf_parent_guidance = [
        "left-roll-op",
        "left-yaw-op",
        "left-pitch-op",
        "left-knee-op",
        "left-tarsus-spring-joint",
        "left-foot-op",
        "right-roll-op",
        "right-yaw-op",
        "right-pitch-op",
        "right-knee-op",
        "right-tarsus-spring-joint",
        "right-foot-op",
    ]


class TalosLoader(RobotLoader):
    path = "talos_data"
    urdf_filename = "talos_reduced.urdf"
    srdf_filename = "talos.srdf"
    free_flyer = True
    has_rotor_parameters = True


class AsrTwoDofLoader(RobotLoader):
    path = "asr_twodof_description"
    urdf_filename = "TwoDofs.urdf"
    urdf_subpath = "urdf"


class TalosBoxLoader(TalosLoader):
    urdf_filename = "talos_reduced_box.urdf"


class TalosFullLoader(TalosLoader):
    urdf_filename = "talos_full_v2.urdf"


class TalosFullBoxLoader(TalosLoader):
    urdf_filename = "talos_full_v2_box.urdf"


class TalosArmLoader(TalosLoader):
    urdf_filename = "talos_left_arm.urdf"
    free_flyer = False


class TalosLegsLoader(TalosLoader):
    def __init__(self, verbose=False):
        super(TalosLegsLoader, self).__init__(verbose=verbose)
        legMaxId = 14
        m1 = self.robot.model
        m2 = pin.Model()
        for j, M, name, parent, Y in zip(
            m1.joints, m1.jointPlacements, m1.names, m1.parents, m1.inertias
        ):
            if j.id < legMaxId:
                jid = m2.addJoint(parent, getattr(pin, j.shortname())(), M, name)
                idx_q, idx_v = m2.joints[jid].idx_q, m2.joints[jid].idx_v
                m2.upperPositionLimit[idx_q : idx_q + j.nq] = m1.upperPositionLimit[
                    j.idx_q : j.idx_q + j.nq
                ]
                m2.lowerPositionLimit[idx_q : idx_q + j.nq] = m1.lowerPositionLimit[
                    j.idx_q : j.idx_q + j.nq
                ]
                m2.velocityLimit[idx_v : idx_v + j.nv] = m1.velocityLimit[
                    j.idx_v : j.idx_v + j.nv
                ]
                m2.effortLimit[idx_v : idx_v + j.nv] = m1.effortLimit[
                    j.idx_v : j.idx_v + j.nv
                ]
                assert jid == j.id
                m2.appendBodyToJoint(jid, Y, pin.SE3.Identity())

        upperPos = m2.upperPositionLimit
        upperPos[:7] = 1
        m2.upperPositionLimit = upperPos
        lowerPos = m2.lowerPositionLimit
        lowerPos[:7] = -1
        m2.lowerPositionLimit = lowerPos
        effort = m2.effortLimit
        effort[:6] = np.inf
        m2.effortLimit = effort

        # q2 = self.robot.q0[:19]
        for f in m1.frames:
            if f.parent < legMaxId:
                m2.addFrame(f)

        g2 = pin.GeometryModel()
        for g in self.robot.visual_model.geometryObjects:
            if g.parentJoint < 14:
                g2.addGeometryObject(g)

        self.robot.model = m2
        self.robot.data = m2.createData()
        self.robot.visual_model = g2
        # self.robot.q0=q2
        self.robot.visual_data = pin.GeometryData(g2)

        # Load SRDF file
        self.robot.q0 = readParamsFromSrdf(
            self.robot.model,
            self.srdf_path,
            self.verbose,
            self.has_rotor_parameters,
            self.ref_posture,
        )

        assert (m2.armature[:6] == 0.0).all()
        # Add the free-flyer joint limits to the new model
        self.addFreeFlyerJointLimits()


class HyQLoader(RobotLoader):
    path = "hyq_description"
    urdf_filename = "hyq_no_sensors.urdf"
    srdf_filename = "hyq.srdf"
    ref_posture = "standing"
    free_flyer = True


class BoltLoader(RobotLoader):
    path = "bolt_description"
    urdf_filename = "bolt.urdf"
    srdf_filename = "bolt.srdf"
    ref_posture = "standing"
    free_flyer = True


class BorinotLoader(RobotLoader):
    path = "borinot_description"
    urdf_subpath = "urdf"
    srdf_subpath = "srdf"
    urdf_filename = "borinot_flying_arm_2.urdf"
    srdf_filename = "borinot_flying_arm_2.srdf"
    ref_posture = "home"
    free_flyer = True


class Solo8Loader(RobotLoader):
    path = "solo_description"
    urdf_filename = "solo.urdf"
    srdf_filename = "solo.srdf"
    ref_posture = "standing"
    free_flyer = True


class Solo12Loader(Solo8Loader):
    urdf_filename = "solo12.urdf"


class FingerEduLoader(RobotLoader):
    path = "finger_edu_description"
    urdf_filename = "finger_edu.urdf"
    srdf_filename = "finger_edu.srdf"
    ref_posture = "hanging"
    free_flyer = False


class KinovaLoader(RobotLoader):
    path = "kinova_description"
    urdf_filename = "kinova.urdf"
    srdf_filename = "kinova.srdf"
    ref_posture = "arm_up"


class TiagoLoader(RobotLoader):
    path = "tiago_description"
    urdf_filename = "tiago.urdf"


class TiagoDualLoader(TiagoLoader):
    urdf_filename = "tiago_dual.urdf"


class TiagoNoHandLoader(TiagoLoader):
    urdf_filename = "tiago_no_hand.urdf"


class ICubLoader(RobotLoader):
    path = "icub_description"
    urdf_filename = "icub.urdf"
    srdf_filename = "icub.srdf"
    free_flyer = True


class ICubReducedLoader(ICubLoader):
    urdf_filename = "icub_reduced.urdf"


class PandaLoader(RobotLoader):
    path = "panda_description"
    urdf_filename = "panda.urdf"
    urdf_subpath = "urdf"
    srdf_filename = "panda.srdf"
    ref_posture = "default"


class AllegroRightHandLoader(RobotLoader):
    path = "allegro_hand_description"
    urdf_filename = "allegro_right_hand.urdf"
    urdf_subpath = "urdf"


class AllegroLeftHandLoader(RobotLoader):
    path = "allegro_hand_description"
    urdf_filename = "allegro_left_hand.urdf"
    urdf_subpath = "urdf"


class UR3Loader(RobotLoader):
    path = "ur_description"
    urdf_filename = "ur3_robot.urdf"
    urdf_subpath = "urdf"
    ref_posture = None


class UR3GripperLoader(UR3Loader):
    urdf_filename = "ur3_gripper.urdf"
    srdf_filename = "ur3_gripper.srdf"


class UR3LimitedLoader(UR3Loader):
    urdf_filename = "ur3_joint_limited_robot.urdf"


class UR5Loader(UR3Loader):
    urdf_filename = "ur5_robot.urdf"
    srdf_filename = "ur5.srdf"


class UR5GripperLoader(UR5Loader):
    urdf_filename = "ur5_gripper.urdf"
    srdf_filename = "ur5_gripper.srdf"


class UR5LimitedLoader(UR5Loader):
    urdf_filename = "ur5_joint_limited_robot.urdf"


class UR10Loader(UR3Loader):
    urdf_filename = "ur10_robot.urdf"


class UR10LimitedLoader(UR10Loader):
    urdf_filename = "ur10_joint_limited_robot.urdf"


class HectorLoader(RobotLoader):
    path = "hector_description"
    urdf_filename = "quadrotor_base.urdf"
    free_flyer = True


class HextiltLoader(RobotLoader):
    path = "hextilt_description"
    urdf_subpath = "urdf"
    srdf_subpath = "srdf"
    urdf_filename = "hextilt_flying_arm_5.urdf"
    srdf_filename = "hextilt_flying_arm_5.srdf"
    ref_posture = "home"
    free_flyer = True


class DoublePendulumLoader(RobotLoader):
    path = "double_pendulum_description"
    urdf_filename = "double_pendulum.urdf"
    urdf_subpath = "urdf"


class DoublePendulumContinuousLoader(DoublePendulumLoader):
    urdf_filename = "double_pendulum_continuous.urdf"


class DoublePendulumSimpleLoader(DoublePendulumLoader):
    urdf_filename = "double_pendulum_simple.urdf"


class QuadrupedLoader(RobotLoader):
    path = "quadruped_description"
    urdf_subpath = "urdf"
    urdf_filename = "quadruped.urdf"
    free_flyer = True


class RomeoLoader(RobotLoader):
    path = "romeo_description"
    urdf_filename = "romeo.urdf"
    urdf_subpath = "urdf"
    free_flyer = True


class SimpleHumanoidLoader(RobotLoader):
    path = "simple_humanoid_description"
    urdf_subpath = "urdf"
    urdf_filename = "simple_humanoid.urdf"
    srdf_filename = "simple_humanoid.srdf"
    free_flyer = True


class SimpleHumanoidClassicalLoader(SimpleHumanoidLoader):
    urdf_filename = "simple_humanoid_classical.urdf"
    srdf_filename = "simple_humanoid_classical.srdf"


class IrisLoader(RobotLoader):
    path = "iris_description"
    # urdf_filename = "iris_simple.urdf"
    urdf_filename = "iris_pepms.urdf"
    free_flyer = True

# New classes from PepMs
class Hexacopter680FlyingArm2Loader(RobotLoader):
    path = "hexacopter680_description"
    urdf_filename = "hexacopter680_flying_arm_2.urdf"
    urdf_subpath = "urdf"
    free_flyer = True


class FlyingArm5Loader(RobotLoader):
    path = "flying_arm_5_description"
    urdf_filename = "flying_arm_5.urdf"
    urdf_subpath = "urdf"
    free_flyer = False


class FlyingArm3Loader(RobotLoader):
    path = "flying_arm_3_description"
    urdf_filename = "flying_arm_3.urdf"
    urdf_subpath = "urdf"
    free_flyer = False


class HexTiltLoader(RobotLoader):
    path = "hextilt_description"
    urdf_filename = "hextilt.urdf"
    urdf_subpath = "urdf"
    free_flyer = True


class HexTiltFlyingArm5(RobotLoader):
    path = "hextilt_description"
    urdf_filename = "hextilt_flying_arm_5.urdf"
    urdf_subpath = "urdf"
    free_flyer = True


class Hexacopter370Loader(RobotLoader):
    path = "hexacopter370_description"
    urdf_filename = "hexacopter370.urdf"
    urdf_subpath = "urdf"
    free_flyer = True


class Hexacopter370FlyingArm3Loader(RobotLoader):
    path = "hexacopter370_description"
    urdf_filename = "hexacopter370_flying_arm_3.urdf"
    urdf_subpath = "urdf"
    free_flyer = True

class Hexacopter370FlyingArm1Loader(RobotLoader):
    path = "hexacopter370_description"
    urdf_filename = "hexacopter370_flying_arm_1.urdf"
    urdf_subpath = "urdf"
    free_flyer = True

class Hexacopter370FlyingArm5Loader(RobotLoader):
    path = "hexacopter370_description"
    urdf_filename = "hexacopter370_flying_arm_5.urdf"
    urdf_subpath = "urdf"
    free_flyer = True
    
class S500UAMLoader(RobotLoader):
    path = "s500_description/s500_uam"
    urdf_filename = "s500_uam.urdf"
    urdf_subpath = "urdf"
    free_flyer = True
    
class S500Loader(RobotLoader):
    path = "s500_description/s500_quadrotor"
    urdf_filename = "s500_quadrotor.urdf"
    urdf_subpath = "urdf"
    free_flyer = True
    
class S500UAMSimpleLoader(RobotLoader):
    path = "s500_description/s500_uam"
    urdf_filename = "s500_uam_simple.urdf"
    urdf_subpath = "urdf"
    free_flyer = True


ROBOTS = {
    "b1": B1Loader,
    "go1": Go1Loader,
    "a1": A1Loader,
    "z1": Z1Loader,
    "b1_z1": B1Z1Loader,
    "anymal": ANYmalLoader,
    "anymal_c": ANYmalCLoader,
    "anymal_kinova": ANYmalKinovaLoader,
    "asr_twodof": AsrTwoDofLoader,
    "baxter": BaxterLoader,
    "cassie": CassieLoader,
    "double_pendulum": DoublePendulumLoader,
    "double_pendulum_continuous": DoublePendulumContinuousLoader,
    "double_pendulum_simple": DoublePendulumSimpleLoader,
    "hector": HectorLoader,
    "hextilt": HextiltLoader,
    "hyq": HyQLoader,
    "icub": ICubLoader,
    "icub_reduced": ICubReducedLoader,
    "iris": IrisLoader,
    "kinova": KinovaLoader,
    "laikago": LaikagoLoader,
    "panda": PandaLoader,
    "allegro_right_hand": AllegroRightHandLoader,
    "allegro_left_hand": AllegroLeftHandLoader,
    "quadruped": QuadrupedLoader,
    "romeo": RomeoLoader,
    "simple_humanoid": SimpleHumanoidLoader,
    "simple_humanoid_classical": SimpleHumanoidClassicalLoader,
    "bolt": BoltLoader,
    "borinot": BorinotLoader,
    "solo8": Solo8Loader,
    "solo12": Solo12Loader,
    "finger_edu": FingerEduLoader,
    "talos": TalosLoader,
    "talos_box": TalosBoxLoader,
    "talos_arm": TalosArmLoader,
    "talos_legs": TalosLegsLoader,
    "talos_full": TalosFullLoader,
    "talos_full_box": TalosFullBoxLoader,
    "tiago": TiagoLoader,
    "tiago_dual": TiagoDualLoader,
    "tiago_no_hand": TiagoNoHandLoader,
    "ur3": UR5Loader,
    "ur3_gripper": UR3GripperLoader,
    "ur3_limited": UR3LimitedLoader,
    "ur5": UR5Loader,
    "ur5_gripper": UR5GripperLoader,
    "ur5_limited": UR5LimitedLoader,
    "ur10": UR10Loader,
    "ur10_limited": UR10LimitedLoader,
    # New classes from PepMs
    'flying_arm_5': FlyingArm5Loader,
    'flying_arm_3': FlyingArm3Loader,
    'hexacopter370': Hexacopter370Loader,
    'hexacopter370_flying_arm_5': Hexacopter370FlyingArm5Loader,
    'hexacopter370_flying_arm_3': Hexacopter370FlyingArm3Loader,
    'hexacopter370_flying_arm_1': Hexacopter370FlyingArm1Loader,
    'hexacopter680_flying_arm_2': Hexacopter680FlyingArm2Loader,
    'hextilt': HexTiltLoader,
    'hextilt_flying_arm_5': HexTiltFlyingArm5,
    's500_uam': S500UAMLoader,
    's500_uam_simple': S500UAMSimpleLoader,
    's500_quadrotor': S500Loader,
}


def loader(name, display=False, rootNodeName="", verbose=False):
    """Load a robot by its name, and optionally display it in a viewer."""
    if name not in ROBOTS:
        robots = ", ".join(sorted(ROBOTS.keys()))
        raise ValueError(
            "Robot '%s' not found. Possible values are %s" % (name, robots)
        )
    inst = ROBOTS[name](verbose=verbose)
    if display:
        if rootNodeName:
            inst.robot.initViewer()
            inst.robot.viz.loadViewerModel(rootNodeName=rootNodeName)
        else:
            inst.robot.initViewer(loadModel=True)
        inst.robot.display(inst.robot.q0)
    return inst


def load(name, display=False, rootNodeName="", verbose=False):
    """Load a robot by its name, and optionnaly display it in a viewer."""
    return loader(name, display, rootNodeName, verbose).robot


def load_full(name, display=False, rootNodeName="", verbose=False):
    """Load a robot by its name, optionnaly display it in a viewer,
    and provide its q0 and paths."""
    inst = loader(name, display, rootNodeName, verbose)
    return inst.robot, inst.robot.q0, inst.df_path, inst.srdf_path
