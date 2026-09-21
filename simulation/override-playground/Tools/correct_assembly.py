"""Explicit, reversible simulation-copy placement changes in FreeCAD millimeters.

Call after neutral parallel transforms have been recovered. No source file is saved.
Geometry edits are a proposed simulation mounting layout, not hardware validation.
"""
import FreeCAD as A
import Part

def apply(document):
    ledger=[]
    def move(name, delta, reason):
        obj=document.getObject(name)
        if obj is None: raise ValueError('Missing correction object '+name)
        before=A.Placement(obj.Placement)
        after=A.Placement(before);after.Base=after.Base+A.Vector(*delta)
        obj.Placement=after
        if 'NeutralPlacement' in obj.PropertiesList:obj.NeutralPlacement=after
        ledger.append(dict(object=name,label=obj.Label,translationMm=list(delta),
                           originalPositionMm=list(before.Base),correctedPositionMm=list(after.Base),reason=reason))
    # Existing half-inch hole pitch; narrow the upper rail mounting by one hole per side.
    for obj in document.UpperStage.Group:
        if ('parallel lift arm' in obj.Label.lower() or 'arm bearing' in obj.Label.lower()
                or obj.Name in ['I_screw'+str(i).zfill(3) for i in range(72,88)]):
            x=obj.Placement.Base.x
            move(obj.Name,(-12.7 if x>0 else 12.7,0,0),'Upper rail and bearing mounting moved inward one hole to clear fixed uprights')
    # Move both lower ladder ties to the rear end where stages do not cross.
    for names,dy in [(['I_channel3_004','I_screw068','I_screw069'],165.1),
                     (['I_channel3_005','I_screw070','I_screw071'],12.7)]:
        for name in names:move(name,(0,dy,0),'Lower ladder tie and fasteners relocated behind the upper-stage swept volume')
    for name in ['I_channel3_004','I_screw068','I_screw069','I_channel3_005','I_screw070','I_screw071']:
        move(name,(0,0,-88.9),'Rear tie remounted on the lower parallel arm')
        document.getObject(name).ParallelOffset=0
    for name,dz in [('I_channel3_003',-279.4),('I_channel3_23',-330.2)]:
        move(name,(0,50.8,dz),'Tower tie relocated to lower mounting holes below the moving-stage envelope')
    move('I_channel3_25',(0,139.7,0),'Front chassis crossmember moved rearward to clear lowered jaws and intake rollers')
    for side in [-1,1]:
        name='SimulationTowerPlate'+('L' if side<0 else 'R')
        plate=document.addObject('PartDesign::Feature',name)
        plate.Label='Simulation mounting plate - tower tie setback'
        x=side*158.75-1.6
        shape=Part.makeBox(3.2,127.0,76.2,A.Vector(x,-139.7,63.5))
        for y in [-127,-76.2]:
            for z in [76.2,114.3]:
                hole=Part.makeCylinder(2.1,5.2,A.Vector(x-1,y,z),A.Vector(1,0,0))
                shape=shape.cut(hole)
        plate.Shape=shape
        document.Tower.addObject(plate)
        ledger.append(dict(object=name,reason='New 3.2 mm simulation adapter plate supports relocated tower ties',hardwareValidated=False))
    for name in ['I_cylinder25','I_cylinder001']:
        move(name,(0,0,25.4),'Release cylinders raised above rotating wheel gear envelopes')
    for name in ['I_channel3_007','I_screw092','I_screw093']:
        move(name,(0,-25.4,0),'Upper distal tie moved away from claw carriage uprights')
    for name,angle in [('I_gear016',3.4),('I_gear018',-.4),('I_gear019',-3.0)]:
        obj=document.getObject(name);pl=A.Placement(obj.Placement)
        pl.Rotation=A.Rotation(A.Vector(0,0,1),angle).multiply(pl.Rotation);obj.Placement=pl
        ledger.append(dict(object=name,rotationDegrees=angle,reason='Phase equal-size meshing gears to remove tooth overlap'))
    # Place jaw channels outside the axial wheel/gear envelopes.
    for group_name in ['LeftJaw','RightJaw']:
        group=document.getObject(group_name)
        for obj in list(group.Group):
            if obj.TypeId=='App::Part':continue
            if not hasattr(obj,'Placement'):continue
            if obj.Label.startswith('White nylon upper-jaw spacer'):
                move(obj.Name,(0,0,12.7),'Upper jaw spacer follows raised support')
            elif obj.Placement.Base.z < -60:
                move(obj.Name,(0,0,-12.7),'Lower jaw support and fasteners clear bottom wheel')
            elif obj.Placement.Base.z > 50:
                move(obj.Name,(0,0,12.7),'Upper jaw support and fasteners clear gear thickness')
    for names in [['I_claw_wheel003','I_collar025','ClawDetail004'],['I_claw_wheel007','I_collar029','ClawDetail012']]:
        for name in names:move(name,(0,0,25.4),'Top wheel and end hardware spaced above raised jaw support')
    for name in ['I_channel2_19','I_channel2_017','I_channel2_018']:
        move(name,(0,12.7,0),'Carriage ties seat against upright face and clear swinging wheels')
    for name in ['I_cylinder25','I_cylinder001']:
        move(name,(0,50.8,0),'Release cylinder moved behind jaw swept volume')
    for name in ['I_elbow','I_elbow001','Detail073','Detail074']:
        move(name,(0,50.8,25.4),'Cylinder fitting and provisional tubing follow cylinder mount')
    for name in ['I_motor006','I_motor007','I_gear84','I_gear011','I_pinion12','I_pinion001']:
        move(name,(0,0,50.8),'Lift drive assembly raised four mounting holes clear of front drivetrain wheels')
    for names in [['I_channel3_004','I_screw068','I_screw069'],['I_channel3_005','I_screw070','I_screw071']]:
        anchor=document.getObject(names[0]).Placement.Base.y
        transform=A.Placement(A.Vector(0,anchor,-12.7),A.Rotation(A.Vector(1,0,0),180)).multiply(A.Placement(A.Vector(0,-anchor,0),A.Rotation()))
        for name in names:
            obj=document.getObject(name);obj.Placement=transform.multiply(obj.Placement)
            if 'NeutralPlacement' in obj.PropertiesList:obj.NeutralPlacement=obj.Placement
            ledger.append(dict(object=name,reason='Tie and fasteners remounted on underside of lower arm to clear rear brace sweep'))
    def replace_geometry(obj,shape,reason):
        original=A.Placement(obj.Placement)
        if obj.TypeId=='App::Link':
            prototype=document.addObject('PartDesign::Feature','SimulationGeometry_'+obj.Name)
            prototype.Label='Simulation geometry prototype - '+obj.Label
            prototype.Shape=shape
            obj.LinkedObject=prototype
            obj.Placement=original
        else:
            obj.Shape=shape;obj.Placement=original
        ledger.append(dict(object=obj.Name,reason=reason,geometryModified=True))
    # Clearance bores at the real shaft axes, rather than hidden shaft/channel overlaps.
    for name in ['I_channel2_07','I_channel2_019','I_channel2_020','I_channel2_021']:
        obj=document.getObject(name);source=obj.LinkedObject if obj.TypeId=='App::Link' else obj
        shape=source.Shape.copy();shape.Placement=A.Placement()
        inv=obj.Placement.inverse()
        for y in [0,-63.501181091378136]:
            start=inv.multVec(A.Vector(0,y,-150));axis=inv.Rotation.multVec(A.Vector(0,0,1))
            shape=shape.cut(Part.makeCylinder(3.3,300,start,axis))
        replace_geometry(obj,shape,'6.6 mm clearance bores through jaw support at pivot and wheel shaft axes')
    for name in ['ClawDetail003','ClawDetail011']:
        obj=document.getObject(name);shape=obj.Shape.copy();shape.Placement=A.Placement()
        shape=shape.common(Part.makeBox(100,100,207,A.Vector(-50,-50,-150)))
        replace_geometry(obj,shape,'Wheel-gear spacer shortened to end at 57 mm below raised jaw support')
    for name in ['Detail034','Detail041']:
        obj=document.getObject(name)
        replace_geometry(obj,Part.makeBox(4.18,4.18,220,A.Vector(-2.09,-2.09,0)),'Estimated 4.18 mm square shaft extended for spaced wheel stack')
        pl=A.Placement(obj.Placement);pl.Base.z=-92;obj.Placement=pl
    for name in ['I_gear36','I_gear002','I_gear004','I_gear006','I_gear008','I_gear010']:
        obj=document.getObject(name);pl=A.Placement(obj.Placement)
        pl.Rotation=A.Rotation(A.Vector(1,0,0),5).multiply(pl.Rotation);obj.Placement=pl
        ledger.append(dict(object=name,rotationDegrees=5,reason='Half-tooth phase offset for 36T motor gear'))
    for name in ['I_channel3_33','I_channel3_002']:
        move(name,(0,0,12.7),'Tower upright raised one mounting hole clear of front motor gear teeth')
    for names,dy in [(['I_gear36','I_motor11','I_gear006','I_motor003'],.4),(['I_gear002','I_motor001','I_gear008','I_motor004'],.4),(['I_gear004','I_motor002','I_gear010','I_motor005'],-.4)]:
        for name in names:move(name,(0,dy,0),'0.4 mm center-distance allowance for drivetrain gear backlash')
    for name in ['I_channel3_19','I_screw088','I_screw089']:
        move(name,(0,12.7,0),'Upper proximal tie shifted one mounting hole away from rotating rear cross tie')
    move('I_channel2_19',(0,0,12.7),'Lower claw cross frame raised one mounting hole to clear swinging lower jaw support')
    for names,dx in [(['I_gear60','I_gear36','I_gear001','I_gear002','I_gear003','I_gear004','I_motor11','I_motor001','I_motor002'],3.0),(['I_gear005','I_gear006','I_gear007','I_gear008','I_gear009','I_gear010','I_motor003','I_motor004','I_motor005'],-3.0)]:
        for name in names:move(name,(dx,0,0),'Transmission plane moved inward 3 mm to provide axial wheel sidewall clearance; shaft axes unchanged')
    for name in ['I_motor006','I_motor007','I_gear84','I_gear011','I_pinion12','I_pinion001']:
        move(name,(0,50.8,0),'Lift transmission relocated rearward four mounting holes to clear upper-arm swept volume')

    # Reachable-intake correction. Keep every relocated drive element on its
    # transmission axis and add source-CAD support geometry instead of moving
    # collision hulls independently.
    for name in ['I_motor006','I_motor007','I_gear84','I_gear011','I_pinion12','I_pinion001']:
        move(name,(0,63.5,0),'Complete lift transmission moved rearward five additional holes for lowered-arm clearance')
    for side in [-1,1]:
        name='SimulationLiftTransmissionPlate'+('L' if side<0 else 'R')
        plate=document.addObject('PartDesign::Feature',name)
        plate.Label='Simulation mounting plate - reachable lift transmission'
        x=side*158.75-1.6
        shape=Part.makeBox(3.2,190.5,101.6,A.Vector(x,-127.0,101.6))
        for y in [-76.2,-12.7,36.3]:
            for z in [133.35,172.8]:
                shape=shape.cut(Part.makeCylinder(2.1,5.2,A.Vector(x-1,y,z),A.Vector(1,0,0)))
        plate.Shape=shape
        document.Tower.addObject(plate)
        ledger.append(dict(object=name,reason='New 3.2 mm side plate supports the complete rearward lift motor, pinion and reduction-gear assembly',hardwareValidated=False))

    # The jaw pivot module advances together: rotating jaw subtrees, fixed
    # gears, pivot shafts, pawls and the pneumatic release hardware retain all
    # relative transforms. Two pairs of tabs bridge the new pivot line back to
    # the claw carriage.
    jaw_module=['LeftJaw','RightJaw','LeftClawGear','RightClawGear',
                'Detail035','Detail042','Detail036','Detail043',
                'I_screw110','I_screw115','I_cylinder25','I_cylinder001',
                'I_elbow','I_elbow001','Detail040','Detail047',
                'I_channel2_11','Detail073','Detail074']
    for name in jaw_module:
        move(name,(0,-25.4,0),'Complete jaw pivot and release module advanced two holes while preserving gear, shaft and pawl alignment')
    for side in [-1,1]:
        for level,z in [('Lower',-21.6),('Upper',52.4)]:
            name='SimulationJawPivotTab'+level+('L' if side<0 else 'R')
            tab=document.addObject('PartDesign::Feature',name)
            tab.Label='Simulation mounting plate - advanced jaw pivot'
            x=side*31.75-19.05
            shape=Part.makeBox(38.1,25.4,3.2,A.Vector(x,-50.8,z))
            for y in [-44.45,-31.75]:
                shape=shape.cut(Part.makeCylinder(2.1,6.0,A.Vector(side*31.75,y,z-1),A.Vector(0,0,1)))
            tab.Shape=shape
            document.Claw.addObject(tab)
            ledger.append(dict(object=name,reason='New 3.2 mm bridge tab supports the advanced jaw pivot shaft from the existing carriage',hardwareValidated=False))
    move('I_channel2_19',(0,0,50.8),'Lower claw cross frame raised four additional holes to clear the expanded jaw sweep')

    # The front motor housings move inward along their output axes. A direct
    # extension shaft crosses the lowered claw upright, so retain the outer
    # driven-gear plane with a two-chain dogleg through a forward jackshaft.
    for name,dx in [('I_motor11',50.8),('I_motor003',-50.8)]:
        move(name,(dx,0,0),'Front drivetrain motor moved inward along its output axis for lowered-jaw clearance')
    for side in [-1,1]:
        suffix='L' if side<0 else 'R'
        shaft=document.addObject('PartDesign::Feature','SimulationFrontMotorJackshaft'+suffix)
        shaft.Label='Simulation front motor forward jackshaft'
        x0=-170.0 if side<0 else 68.4
        shaft.Shape=Part.makeBox(101.6,4.18,4.18,A.Vector(x0,-280.99,39.56))
        document.Chassis.addObject(shaft)
        ledger.append(dict(object=shaft.Name,reason='Estimated 4.18 mm square jackshaft routes the inset motor drive ahead of the lowered claw sweep',hardwareValidated=False))
        for plane,px in [('Inner',side*89.2),('Outer',side*170.0)]:
            chain=document.addObject('PartDesign::Feature','SimulationFrontChain'+plane+suffix)
            chain.Label='Simulation front drivetrain chain run'
            shape=Part.makeBox(2.0,165.0,2.0,A.Vector(px-1.0,-278.9,33.56))
            shape=shape.fuse(Part.makeBox(2.0,165.0,2.0,A.Vector(px-1.0,-278.9,47.74)))
            shape=shape.fuse(Part.makeCylinder(8.09,2.0,A.Vector(px-1.0,-113.9,41.65),A.Vector(1,0,0)))
            shape=shape.fuse(Part.makeCylinder(8.09,2.0,A.Vector(px-1.0,-278.9,41.65),A.Vector(1,0,0)))
            chain.Shape=shape
            document.Chassis.addObject(chain)
            ledger.append(dict(object=chain.Name,reason='Forward chain stage connects the inset motor or retained outer gear plane to the jackshaft',hardwareValidated=False))
            if plane=='Outer':
                for bearing_index,bx in enumerate([px,px+side*12.7]):
                    bearing=document.addObject('PartDesign::Feature','SimulationFrontJackshaftMount'+str(bearing_index)+suffix)
                    bearing.Label='Simulation mounting plate - front jackshaft bearing'
                    bearing.Shape=Part.makeBox(3.2,25.4,25.4,A.Vector(bx-1.6,-291.6,28.95))
                    document.Chassis.addObject(bearing)
                    ledger.append(dict(object=bearing.Name,reason='Paired outboard 3.2 mm bearing plates support the forward drivetrain jackshaft outside the claw sweep',hardwareValidated=False))
        rail=document.addObject('PartDesign::Feature','SimulationFrontJackshaftRail'+suffix)
        rail.Label='Simulation mounting plate - front jackshaft rail'
        rx=side*182.7-1.6
        rail.Shape=Part.makeBox(3.2,152.3,12.7,A.Vector(rx,-291.6,92.7)).fuse(
            Part.makeBox(3.2,25.4,63.75,A.Vector(rx,-291.6,41.65)))
        document.Chassis.addObject(rail)
        ledger.append(dict(object=rail.Name,reason='Outboard side rail ties the forward jackshaft bearing pair back to the chassis above the front wheel envelope',hardwareValidated=False))
        mount=document.addObject('PartDesign::Feature','SimulationFrontMotorMount'+suffix)
        mount.Label='Simulation mounting plate - inset front motor'
        x=side*89.2-1.6
        # Stay inside the motor housing's swept envelope; the first 76.2 mm
        # plate protruded rearward into the lowered claw cross frame.
        mount.Shape=Part.makeBox(3.2,50.8,50.8,A.Vector(x,-139.3,16.25))
        document.Chassis.addObject(mount)
        ledger.append(dict(object=mount.Name,reason='New 3.2 mm inner plate mounts the inset front drivetrain motor to the chassis',hardwareValidated=False))

    move('I_channel3_23',(0,50.8,0),'Lower tower tie moved rearward four additional holes; extended side plates retain its support')
    move('I_channel2_19',(0,-25.4,12.7),'Raised claw cross frame moved one hole forward and up to clear exact upper-arm solids')
    for name in ['I_channel3_004','I_screw068','I_screw069']:
        move(name,(0,101.6,-25.4),'Forward lower-arm tie pack moved to rear hole row and lowered two holes clear of the lift transmission')
    for name in ['I_channel3_005','I_screw070','I_screw071']:
        move(name,(0,50.8,-50.8),'Rear lower-arm tie pack moved to the same rear row and stacked two holes below its mate')
    return ledger
