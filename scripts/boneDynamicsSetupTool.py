import maya.cmds as cmds
import json
from expcol import collider

cmds.loadPlugin("boneDynamicsNode.mll", qt=True)

# 取得するアトリビュートのリストを指定
ATTRIBUTES_TO_EXPORT = [
    'resetTime','fps','rotationOffsetX','rotationOffsetY','rotationOffsetZ',
    'damping','elasticity','elasticForceFunction','gravityMultiply','enableTurbulence',
    'mass','gravityX','gravityY','gravityZ','additionalForceX','additionalForceY','additionalForceZ',
    'additionalForceScale','turbulenceSeed','turbulenceStrength','turbulenceVectorChangeScale',
    'turbulenceVectorChangeMax','enableAngleLimit','angleLimit','radius','iterations',
    'enableGroundCol','groundHeight',
]

BONEDYANMICS_SETTINGS = {
    'radius':'Radius', 'enable':'Enable', 'resetTime':'Reset Time', 'fps':'Fps', 'damping':'Danmping', 'elasticity':'Elasticity', 'stiffness':'Stiffness',
    'mass':'Mass', 'gravityX':'Gravity X', 'gravityY':'Gravity Y', 'gravityZ':'Gravity Z', 'gravityMultiply':'Gravity Multiply',
    'enableAngleLimit':'Enable Angle Limit', 'angleLimit':'Angle Limit', 
}

BONEDYANMICS_TO_CTL = {
    'enable', 'resetTime', 'fps', 'damping', 'elasticity', 'stiffness',
    'mass', 'gravityX', 'gravityY', 'gravityZ', 'gravityMultiply', 'enableAngleLimit', 'angleLimit'
}

HIDE_ATTR = [
    'translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 
    'scaleX', 'scaleY', 'scaleZ', 'visibility'
]

DEFDICT = {
        'radius': 1,
        'resetTime': 0,
        'fps': 30,
        'damping': 0.1,
        'elasticity': 30,
        'stiffness': 0,
        'mass': 1,
        'gravityX': 0,
        'gravityY': -980,
        'gravityZ': 0,
        'gravityMultiply': 0,
        'angleLimit': 60,
}

MINDICT = {
        'radius': 0,
        'fps': 1,
        'damping': 0.1,
        'elasticity': 0,
        'stiffness': 0,
        'mass': 0.001,
        'gravityMultiply': 0,
        'angleLimit': 0,
}

MAXDICT = {
        'damping': 1,
        'stiffness': 1,
        'gravityMultiply': 1,
        'angleLimit': 360,
}

# UIウィンドウを作成
def boneDynamics_setup_ui():

    if cmds.window("boneDynamicsSetup", exists=True):
        cmds.deleteUI("boneDynamicsSetup")

    window = cmds.window(
        "boneDynamicsSetup",
        title="boneDynamics Setup Tool",
        widthHeight=(400, 410),
        sizeable=False
        )

    cmds.columnLayout(adjustableColumn=True)

    tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

    child1 = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 10), rowSpacing=10)
    cmds.text(label="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿")
    # 説明ラベル
    cmds.text(label="アトリビュートを追加するオブジェクトをセットしてください。")
    # ボーンダイナミクスコントローラーを生成
    cmds.textFieldButtonGrp(
        "add_obj",
        buttonLabel="Set",
        adjustableColumn=True,
        buttonCommand=set_objName
        )
    # 説明ラベル
    cmds.text(label="コントローラの接頭語を入力します。")
    cmds.rowLayout(
        nc=2,
        adjustableColumn=True,
        columnAttach=[(2, "both", 0)],
        columnWidth=[(1, 10), (2, 270)]
        )
    cmds.text(label="Front Name :")
    cmds.textField("nametext")
    cmds.setParent("..")
    # 説明ラベル
    cmds.text(label="コントローラーに位置合わせしたジョイントチェーンを作成します。")
    # ボーンダイナミクスコントローラーを生成
    cmds.rowLayout(
        nc=2,
        adjustableColumn=True,
        columnAttach=[(2, "both", 0)],
        columnWidth=[(1, 20), (2, 90)]
        )
    cmds.button(label="Create jointchain to Controller",command="create_dynamics_chain()")
    cmds.button(label="Ctrl Only",command="ctrl_select()")
    cmds.setParent("..")
    # 説明ラベル
    cmds.text(label="ジョイントチェーンにボーンダイナミクスを適応します。")
    # ボーンダイナミクス適応
    cmds.rowLayout(
        nc=2,
        adjustableColumn=True,
        columnAttach=[(2, "both", 0)],
        columnWidth=[(1, 20), (2, 90)]
        )
    cmds.button(label="Apply boneDynamics to jointchain", width=100, command="boneDynamicsCreate()")   
    cmds.button(label="Jnt Only",command="jnt_select()")
    cmds.setParent("..") 
    # 説明ラベル
    cmds.text(label="boneDynamicsNodeをJSON形式でエクスポート/インポートします。")
    # エクスポートボタンを追加
    cmds.button(label="Export Select boneDynamics", width=100, command=lambda x: save_json_ui())    
    # インポートボタンを追加
    cmds.button(label="Import Select boneDynamics", width=100, command=lambda x: load_json_ui())
    cmds.text(label="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿")
    cmds.setParent('..')

    child2 = cmds.columnLayout(adjustableColumn=True, columnAttach=("both", 10), rowSpacing=10)
    cmds.text(label="＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿＿")
    cmds.text(label="ジョイントを選択してから任意のコライダーを選択してください。")
    cmds.rowLayout(
        numberOfColumns=3,
        columnAttach3=('both', 'both', 'both'),
        )
    cmds.iconTextButton(
        image="path/to/sphere.jpg",
        width=120, height=120,
        command=lambda *args: create_colliders(0)
        )
    cmds.iconTextButton(
        image="path/to/capsule.jpg",
        width=120, height=120,
        command=lambda *args: create_colliders(1)
        )
    cmds.iconTextButton(
        image="path/to/capsule2.jpg",
        width=120, height=120,
        command=lambda *args: create_colliders(2)
        )
    cmds.setParent('..')
    cmds.text(label="選択されたboneDynamicsに風向きのコントローラーを生成します。")
    cmds.button(label="Create additional Ctrl", width=100, command=lambda x: create_additionalCtl())
    cmds.setParent('..')

    cmds.tabLayout(
        tabs,
        edit=True,
        tabLabel=((child1, "boneDynamics Settings"),(child2, "Others Settings")),
    )

    cmds.showWindow(window)

# JSONファイルにエクスポート
def export_selected_to_json(filepath):

    selected_objects = cmds.ls(sl=True)
    
    export_data = []

    for obj in selected_objects:
        obj_data = {}
        obj_data['name'] = obj
        obj_data['type'] = cmds.nodeType(obj)

        # 指定したアトリビュートのみを取得
        attributes = {}
        for attr in ATTRIBUTES_TO_EXPORT:
            if cmds.attributeQuery(attr, node=obj, exists=True):
                try:
                    # アトリビュートの値を取得
                    value = cmds.getAttr(f"{obj}.{attr}")
                    attributes[attr] = value
                except:
                    attributes[attr] = "Could not retrieve"

        obj_data['attributes'] = attributes
        export_data.append(obj_data)

    # JSONにエクスポート
    with open(filepath, 'w') as json_file:
        json.dump(export_data, json_file, indent=4)

    print("エクスポート完了: " + filepath)

# JSONファイルをインポートし、選択されたオブジェクトにアトリビュートを適用
def import_json_to_maya(filepath):

    with open(filepath, 'r') as json_file:
        import_data = json.load(json_file)

    # 選択したオブジェクトを取得
    selected_objects = cmds.ls(sl=True)
    
    for obj in selected_objects:
        for obj_data, obj_name in zip(import_data, selected_objects):
            for attr, value in obj_data['attributes'].items():
                try:
                    # アトリビュートの値を設定
                    cmds.setAttr(f"{obj}.{attr}", value)
                except Exception as e:
                    print(f"アトリビュート {attr} の適用に失敗しました: {str(e)}")

    print(f"インポート完了: {filepath}")

# 保存先を選択するUIを表示す
def save_json_ui():

    filepath = cmds.fileDialog2(fileFilter="JSON Files (*.json)", dialogStyle=2, fileMode=0, caption="Export JSON File")
    
    if filepath:
        export_selected_to_json(filepath[0])
    else:
        print("保存先が選択されませんでした。")

# インポートするファイルを選択するUIを表示
def load_json_ui():

    filepath = cmds.fileDialog2(fileFilter="JSON Files (*.json)", dialogStyle=2, fileMode=1, caption="Import JSON File")
    
    if filepath:
        import_json_to_maya(filepath[0])
    else:
        print("ファイルが選択されませんでした。")

# ダイナミクスノードの設定
def create_dynamics_node(
        bone, 
        end, 
        scalable=False, 
        target_bone=None, 
        offset_node=None, 
        colliders=[],
        visualize=True,
        additional_force_node=None, 
        additional_force_init_vec=[0,0,-1]
    ):

    if not bone in cmds.listRelatives(end, p=True):
        print("Exit: {} is not {}'s parent.".format(bone, end))
        return
    
    boneDynamicsNode = cmds.createNode("boneDynamicsNode")

    joint_rot = cmds.xform(bone, q=True, os=True, ro=True)

    cmds.connectAttr('time1.outTime', boneDynamicsNode + '.time', force=True)
    cmds.connectAttr(bone + '.translate', boneDynamicsNode + '.boneTranslate', f=True)
    cmds.connectAttr(bone + '.parentMatrix[0]', boneDynamicsNode + '.boneParentMatrix', f=True)
    cmds.connectAttr(bone + '.parentInverseMatrix[0]', boneDynamicsNode + '.boneParentInverseMatrix', f=True)
    cmds.connectAttr(bone + '.jointOrient', boneDynamicsNode + '.boneJointOrient', f=True)
    cmds.connectAttr(end + '.translate', boneDynamicsNode + '.endTranslate', f=True)
    cmds.connectAttr(boneDynamicsNode + '.outputRotate', bone + '.rotate', f=True)
    
    cmds.setAttr(boneDynamicsNode + '.rotationOffset', *joint_rot)
    
    if scalable:
        cmds.connectAttr(bone + '.scale', boneDynamicsNode + '.boneScale', f=True)
        cmds.connectAttr(bone + '.inverseScale', boneDynamicsNode + '.boneInverseScale', f=True)
        cmds.connectAttr(end + '.scale', boneDynamicsNode + '.endScale', f=True)

    if target_bone:
        if cmds.objExists(target_bone):
            cmds.connectAttr(target_bone + '.rotate', boneDynamicsNode + '.rotationOffset', f=True)

    if offset_node:
        if cmds.objExists(offset_node):
            cmds.connectAttr(offset_node + '.worldMatrix[0]', boneDynamicsNode + '.offsetMatrix', f=True)

    if additional_force_node:
        if cmds.objExists(additional_force_node):
            vp = cmds.listConnections(additional_force_node + '.worldMatrix[0]', s=False, d=True, type='vectorProduct')
            if vp:
                vp = vp[0]
            else:
                vp = cmds.createNode('vectorProduct')
                cmds.setAttr(vp + '.operation', 3)
                cmds.setAttr(vp + '.input1', additional_force_init_vec[0], additional_force_init_vec[1], additional_force_init_vec[2], type='double3')
                cmds.setAttr(vp + '.normalizeOutput', 1)
                cmds.connectAttr(additional_force_node + '.worldMatrix[0]', vp + '.matrix', f=True)
            cmds.connectAttr(vp + '.output', boneDynamicsNode + '.additionalForce', f=True)
                
    if visualize:
        # angle limit
        angle_cone = cmds.createNode("implicitCone")
        angle_cone_tm = cmds.listRelatives(angle_cone, p=True)[0]
        angle_cone_ro = cmds.createNode("transform", n="{}_cone_ro".format(bone))
        angle_cone_root = cmds.createNode("transform", n="{}_cone_root".format(bone))
        cmds.setAttr(angle_cone_tm + '.ry', -90)
        cmds.parent(angle_cone_tm, angle_cone_ro, r=True)
        cmds.parent(angle_cone_ro, angle_cone_root, r=True)
        bone_parent = cmds.listRelatives(bone, p=True)
        if bone_parent:
            cmds.parent(angle_cone_root, bone_parent[0], r=True)
        cmds.connectAttr(boneDynamicsNode + '.boneTranslate', angle_cone_root + '.translate', f=True)
        cmds.connectAttr(boneDynamicsNode + '.boneJointOrient', angle_cone_root + '.rotate', f=True)
        cmds.connectAttr(boneDynamicsNode + '.rotationOffset', angle_cone_ro + '.rotate', f=True)
        cmds.connectAttr(boneDynamicsNode + '.enableAngleLimit', angle_cone_root + '.v', f=True)
        cmds.connectAttr(boneDynamicsNode + '.angleLimit', angle_cone + '.coneAngle', f=True)
        cmds.setAttr(angle_cone + '.coneCap', 2)
        cmds.setAttr(angle_cone_tm + '.overrideEnabled', 1)
        cmds.setAttr(angle_cone_tm + '.overrideDisplayType', 2)

        # collision radius
        radius_sphere = cmds.createNode("implicitSphere")
        cmds.connectAttr(boneDynamicsNode + '.radius', radius_sphere + '.radius', f=True)
        radius_sphere_tm = cmds.listRelatives(radius_sphere, p=True)[0]
        cmds.parent(radius_sphere_tm, end, r=True)
        cmds.setAttr(radius_sphere_tm + '.overrideEnabled', 1)
        cmds.setAttr(radius_sphere_tm + '.overrideDisplayType', 2)
        cmds.connectAttr(boneDynamicsNode + '.iterations', radius_sphere_tm + '.v', f=True)
    
    sphere_col_idx = 0
    capsule_col_idx = 0
    iplane_col_idx = 0
    mesh_col_idx = 0

    for col in colliders:
        
        if not cmds.objExists(col):
            print("Skip: {} is not found.".format(col))
            continue

        if not cmds.attributeQuery('colliderType', n=col, ex=True):
            col_shape = cmds.listRelatives(col, s=True, f=True)
            if col_shape:
                if cmds.nodeType(col_shape[0]) == 'mesh':
                    cmds.connectAttr(col_shape[0] + '.worldMesh[0]', boneDynamicsNode + '.meshCollider[{}]'.format(mesh_col_idx), f=True)
                    mesh_col_idx += 1
                    continue
            print("Skip: {} has no 'colliderType' attribute.".format(col))
            continue

        colliderType = cmds.getAttr(col + '.colliderType')
        
        if colliderType == 'sphere':
            cmds.connectAttr(col + ".worldMatrix[0]", boneDynamicsNode + ".sphereCollider[{}].sphereColMatrix".format(sphere_col_idx), f=True)
            cmds.connectAttr(col + ".radius", boneDynamicsNode + ".sphereCollider[{}].sphereColRadius".format(sphere_col_idx), f=True)
            sphere_col_idx += 1
        
        elif colliderType in ['capsule', 'capsule2']:
            radius_attr_a = ".radius" if colliderType == 'capsule' else ".radiusA"
            radius_attr_b = ".radius" if colliderType == 'capsule' else ".radiusB"
            a = cmds.listConnections(col + '.sphereA', d=0)[0]
            b = cmds.listConnections(col + '.sphereB', d=0)[0]
            cmds.connectAttr(a + ".worldMatrix[0]", boneDynamicsNode + ".capsuleCollider[{}].capsuleColMatrixA".format(capsule_col_idx), f=True)
            cmds.connectAttr(b + ".worldMatrix[0]", boneDynamicsNode + ".capsuleCollider[{}].capsuleColMatrixB".format(capsule_col_idx), f=True)
            cmds.connectAttr(col + radius_attr_a, boneDynamicsNode + ".capsuleCollider[{}].capsuleColRadiusA".format(capsule_col_idx), f=True)
            cmds.connectAttr(col + radius_attr_b, boneDynamicsNode + ".capsuleCollider[{}].capsuleColRadiusB".format(capsule_col_idx), f=True)
            capsule_col_idx += 1
        
        elif colliderType == 'infinitePlane':
            cmds.connectAttr(col + ".worldMatrix[0]", boneDynamicsNode + ".infinitePlaneCollider[{}].infinitePlaneColMatrix".format(iplane_col_idx), f=True)
            iplane_col_idx += 1

    return boneDynamicsNode

# ジョイントチェーンにダイナミクスを適応
def boneDynamicsCreate():
    
    # Select in order from root to tip of the joint-chain.
    joints = cmds.ls(sl=True)
    dynamicsName = cmds.textField("nametext", query=True, text=True)
    
    # Enable per-section scaling.
    scalable = True
    
    # Place the collider created by expcol as a child of 'collider_grp'.
    all_obj = cmds.ls(dag=True, tr=True)
    colliders = [obj for obj in all_obj if "collider" in obj]
    
    # Duplicate the joint-chain to be simulated and add '_target' to the postfix.
    target_bone_postfix = "_target"
    
    # Name of the node to offset the transform.
    offset_node_name = "offset"

    # Node name that controls the direction of additional force
    additional_force_node_name = "wind"
    
    # ---------------------------------------------------

    set_name = "boneDynamicsNodeSet"
    if not cmds.objExists(set_name):
        cmds.select(cl=True)
        cmds.sets(name=set_name)

    for joint in joints:
    
        world_pos = cmds.xform(joint, q=True, ws=True, t=True)

        if not dynamicsName:

            dynm_ctl_name = "dynm_01_ctl"
            cnt = 1

            while cmds.objExists(dynm_ctl_name):
                cnt += 1
                dynm_ctl_name = "dynm_" + f"{cnt:02d}" + "_ctl"
            
        else:

            dynm_ctl_name = dynamicsName + "_dynm_01_ctl"
            cnt = 1

            while cmds.objExists(dynm_ctl_name):
                cnt += 1
                dynm_ctl_name = dynamicsName + "_dynm_" + f"{cnt:02d}" + "_ctl" 

        sph = cmds.sphere(n=dynm_ctl_name, radius=1, sections=1, spans=2)

        if not cmds.objExists("dynmCtlGrp"):
            cmds.createNode("transform", n="dynmCtlGrp")
            cmds.parent("dynmCtlGrp", "dynmGrp", r=False)
        cmds.parent(sph, "dynmCtlGrp", r=False)

        sph_node = sph[0] + "Shape"
        cmds.setAttr(f"{sph_node}.overrideEnabled", 1)
        cmds.setAttr(f"{sph_node}.overrideShading", 0)
        cmds.setAttr(f"{sph_node}.overrideColor", 17)

        cmds.xform(sph[0], ws=True, t=world_pos)

        for attr in HIDE_ATTR:
            cmds.setAttr("{}.{}".format(dynm_ctl_name, attr), keyable=False)

        cmds.addAttr(
            sph,
            longName="dynamicsSetting",
            niceName="__________",
            attributeType="enum",
            enumName="dynamics",
            keyable=1
        )
        for long, nice in BONEDYANMICS_SETTINGS.items():
            sph_attr(
                sph,
                long,
                nice
            )
        cmds.connectAttr(sph[0] + ".radius", sph[1] + ".radius", f=True)

        cmds.parentConstraint(joint, dynm_ctl_name, mo=False)

    for bone, end in zip(joints[:-1], joints[1:]):
        boneDynamicsNode = create_dynamics_node(
            bone, 
            end,
            scalable=scalable, 
            target_bone=bone+target_bone_postfix, 
            offset_node=offset_node_name, 
            colliders=colliders,
            visualize=True,
            additional_force_node=additional_force_node_name,
            additional_force_init_vec=[0, 0, -1]
        )

        if boneDynamicsNode:
            cmds.sets(boneDynamicsNode, addElement=set_name)

        for attr in BONEDYANMICS_TO_CTL:
            test=cmds.connectAttr(sph[0] + "." + attr, boneDynamicsNode + "." + attr, f=True)
            print(test)

# ダイナミクスコントローラーにアトリビュート追加
def sph_attr(
        obj,
        long,
        nice
    ):

    def_Val = DEFDICT.get(long)
    min_Val = MINDICT.get(long)
    max_Val = MAXDICT.get(long, float('inf'))

    if long in ["enableAngleLimit", "enable"]:
        cmds.addAttr(
            obj,
            longName=long,
            niceName=nice,
            attributeType="bool",
            defaultValue=(long == "enable"),
            keyable=True
        )
    elif long in ["radius", "fps", "elasticity", "mass"]:
        cmds.addAttr(
            obj,
            longName=long,
            niceName=nice,
            attributeType="float",
            defaultValue=def_Val,
            minValue=min_Val,
            keyable=True
        )
    elif long in ["danping", "stiffness", "gravityMultiply", "angleLimit"]:
        cmds.addAttr(
            obj,
            longName=long,
            niceName=nice,
            attributeType="float",
            defaultValue=def_Val,
            minValue=min_Val,
            maxValue=max_Val,
            keyable=True
        )
    else:
        cmds.addAttr(
            obj,
            longName=long,
            niceName=nice,
            attributeType="float",
            defaultValue=def_Val,
            keyable=True
        )

# コントローラーに位置合わせしたジョイントチェーンを作成
def create_dynamics_chain(constraint=True):

    nodes = cmds.ls(sl=True)
    attributeObj = cmds.textFieldButtonGrp("add_obj", query=True, text=True)
    dynamicsName = cmds.textField("nametext", query=True, text=True)

    if not nodes:
        return 

    create_attribute()
    
    if not cmds.objExists("dynmGrp"):
        cmds.createNode("transform", n="dynmGrp")
    if not cmds.objExists("dynmJntGrp"):
        joint_root = cmds.createNode("transform", n="dynmJntGrp")
        cmds.parent(joint_root, "dynmGrp", relative=True)
    else:
        joint_root = cmds.ls("*dynmJntGrp*")

    # ルートコンストレイント
    node_parent = cmds.listRelatives(nodes[0], p=True)
    if node_parent:
        world_mtx = cmds.xform(node_parent[0], q=True, ws=True, m=True)

    # ダイナミクス用のジョイントチェーン作成
    joint_list = []
    pr = joint_root
    for i, node in enumerate(nodes):
        cmds.select(cl=True)

        world_pos = cmds.xform(node, q=True, ws=True, rp=True)

        if not dynamicsName:

            jnt_name = "dynmJnt_01"
            cnt = 1

            while cmds.objExists(jnt_name):
                cnt += 1
                jnt_name = "dynmJnt_" + f"{cnt:02d}"
        
        else:

            jnt_name = dynamicsName + "_dynmJnt_01"
            cnt = 1

            while cmds.objExists(jnt_name):
                cnt += 1
                jnt_name = dynamicsName + "_dynmJnt_" + f"{cnt:02d}"
        
        jnt = cmds.joint(n=jnt_name, p=world_pos)
        cmds.setAttr(jnt + '.radius', 11)
        cmds.setAttr(jnt + '.useOutlinerColor', True)
        cmds.setAttr(jnt + '.outlinerColor', 0, 1, .5)
        cmds.setAttr(jnt + '.overrideEnabled', True)
        cmds.setAttr(jnt + '.overrideDisplayType', 0)
        cmds.setAttr(jnt + '.overrideRGBColors', False)
        cmds.setAttr(jnt + '.overrideColor', 27)

        if pr:
            cmds.parent(jnt, pr, r=False)
        pr = jnt

        joint_list.append([node, jnt])

    # ジョイントの方向を調整
    for _, jnt in joint_list:
        if cmds.listRelatives(jnt, c=True):
            cmds.joint(jnt, e=True, oj='xzy', sao='zup', zso=True)
        else:
            cmds.joint(jnt, e=True, oj='none')

    # コンストレイント
    if constraint:
        for i, (node, jnt) in enumerate(joint_list):
            if i >= len(nodes):  # インデックス範囲をチェック
                break
            
            cons = cmds.orientConstraint(jnt, node, mo=True)
            pb = cmds.createNode('pairBlend')
            cmds.connectAttr(attributeObj + ".DynamicsIntencity", '{}.weight'.format(pb), f=True)
            
            for at in 'XYZ':
                cmds.connectAttr(
                    '{}.constraintRotate{}'.format(cons[0], at),
                    '{}.inRotate{}2'.format(pb, at),
                    f=True
                )
                cmds.connectAttr(
                    '{}.outRotate{}'.format(pb, at),
                    '{}.rotate{}'.format(node, at),
                    f=True
                )

    return [jnt for _, jnt in joint_list]

# ダイナミクスの強度を変更するアトリビュート作成
def create_attribute():

    attr_ctl = cmds.textFieldButtonGrp("add_obj", query=True, text=True)

    if not attr_ctl:
        print("オブジェクトがセットされていません")
        return

    cmds.addAttr(
        attr_ctl, 
        longName="DynamicsIntencity",
        niceName="Dynamics Intencity",
        attributeType="bool",
        defaultValue=True,
        keyable=True
        )

# テキストフィールドに選択したオブジェクトをセット
def set_objName():

    slc = cmds.ls(sl=True, type="transform")
    if slc:
        cmds.textFieldButtonGrp("add_obj", edit=True, text=slc[0])

# コライダーを生成
def create_colliders(num):

    slc = cmds.ls(sl=True)

    if slc:

        slc = slc[0]
        base_pos = cmds.xform(slc, q=True, ws=True, t=True)
        new_name = slc + "_collider_01"
        cnt = 1

        while cmds.objExists(new_name):
            cnt += 1
            new_name = slc + "_collider_" + f"{cnt:02d}"

        if num == 0:
            col=collider.sphere()
        elif num == 1:
            col=collider.capsule()
        elif num == 2:
            col=collider.capsule2()

        rename_col = cmds.rename(col, new_name)
        cmds.setAttr(rename_col + ".translate", *base_pos)
        cmds.parent(rename_col, slc)

    else:
        print("１つオブジェクトを選択してください。")

# 追加力/乱流力の追加
def create_additionalCtl():

    slc = cmds.ls(sl=True, type="boneDynamicsNode")
    node = cmds.createNode("vectorProduct")

    ctl = cmds.curve(
        d=1,
        p=[(-0.2745556182141273, 0.0, 1.0982224728565093), (-0.2745556182141273, 0.0, -0.27455561821413355), (-0.8236668546423819, 0.0, -0.27455561821413355), (0.0, 0.0, -1.0982224728565093), (0.8236668546423819, 0.0, -0.27455561821413355), (0.2745556182141273, 0.0, -0.27455561821413355), (0.2745556182141273, 0.0, 1.0982224728565093), (-0.2745556182141273, 0.0, 1.0982224728565093)],
        n="additional_Ctl"
            )
    cmds.group(ctl, n="additional_grp")
    cmds.xform(ctl, translation=(0, 0, 0), worldSpace=True)
    cmds.xform(ctl, centerPivots=True)

    cmds.addAttr(
        ctl,
        longName="dynamicsSetting",
        niceName="__________",
        attributeType="enum",
        enumName="dynamics",
        keyable=1
        )
    cmds.addAttr(
        ctl,
        longName="additionalForceScale",
        niceName="Additional Force Scale",
        attributeType="float",
        defaultValue=1.0,
        keyable=1
        )
    cmds.addAttr(
        ctl,
        longName="enableTurbulence",
        niceName="Enable Turbulence",
        attributeType="enum",
        enumName="off:on",
        keyable=1
        )
    cmds.addAttr(
        ctl,
        longName="turbulenceSeed",
        niceName="Turbulence Seed",
        attributeType="float",
        defaultValue=1.0,
        keyable=1
        )
    cmds.addAttr(
        ctl,
        longName="turbulenceStrength",
        niceName="Turbulence Strength",
        attributeType="float",
        defaultValue=10.0,
        keyable=1
        )
    cmds.addAttr(
        ctl,
        longName="turbulenceVectorChangeScale",
        niceName="Turbulence Vector Change Scale",
        attributeType="float",
        defaultValue=0.05,
        keyable=1
        )
    cmds.addAttr(
        ctl,
        longName="turbulenceVectorChangeMax",
        niceName="Turbulence Vector Change Max",
        attributeType="float",
        defaultValue=0.1,
        keyable=1
        )
    
    cmds.connectAttr(ctl + ".worldMatrix", node + ".matrix", f=True)
    cmds.setAttr(node + ".operation", 3)
    cmds.setAttr(node + ".input1Z", -1)
    cmds.setAttr(node + ".normalizeOutput", 1)

    for sl in slc:
        
        cmds.connectAttr(node + ".output", sl + ".additionalForce", f=True)
        cmds.connectAttr(ctl + ".additionalForceScale", sl + ".additionalForceScale", f=True)
        cmds.connectAttr(ctl + ".enableTurbulence", sl + ".enableTurbulence", f=True)
        cmds.connectAttr(ctl + ".turbulenceSeed", sl + ".turbulenceSeed", f=True)
        cmds.connectAttr(ctl + ".turbulenceStrength", sl + ".turbulenceStrength", f=True)
        cmds.connectAttr(ctl + ".turbulenceVectorChangeScale", sl + ".turbulenceVectorChangeScale", f=True)
        cmds.connectAttr(ctl + ".turbulenceVectorChangeMax", sl + ".turbulenceVectorChangeMax", f=True)

# 選択階層下のコントローラーのみ選択
def ctrl_select():
    slc = cmds.ls(sl=True, dag=True)
    ctl = []
    for obj in slc:
        curves = cmds.ls(obj, dag=True, type="nurbsCurve")
        ctl.extend(curves)
    cmds.select(cmds.listRelatives(ctl, p=True))

# 選択階層下のジョイントのみ選択
def jnt_select():
    jnt = cmds.ls(sl=True, dag=True, type="transform")
    cmds.select(jnt)

# UIを表示
boneDynamics_setup_ui()