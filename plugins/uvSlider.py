# =====================================================================
#
# Author : Ryan Roberts
# email: ryan@artofrigging.com
#
# =====================================================================

import sys
import maya.OpenMaya as OpenMaya
import maya.OpenMayaMPx as OpenMayaMPx
import maya.cmds as cmds

import math

nodeName= "uvSlider"
nodeId = OpenMaya.MTypeId(0x103ffe)

kApiVersion = cmds.about(apiVersion=True)
if kApiVersion < 201600:
		kInput = OpenMayaMPx.cvar.MPxDeformerNode_input
		kInputGeom = OpenMayaMPx.cvar.MPxDeformerNode_inputGeom
		kOutputGeom = OpenMayaMPx.cvar.MPxDeformerNode_outputGeom
		kEnvelope = OpenMayaMPx.cvar.MPxDeformerNode_envelope
else:
		kInput = OpenMayaMPx.cvar.MPxGeometryFilter_input
		kInputGeom = OpenMayaMPx.cvar.MPxGeometryFilter_inputGeom
		kOutputGeom = OpenMayaMPx.cvar.MPxGeometryFilter_outputGeom
		kEnvelope = OpenMayaMPx.cvar.MPxGeometryFilter_envelope


class uvSlider(OpenMayaMPx.MPxDeformerNode):
	idCallback = []

	inputSurface = OpenMaya.MObject()
	inputBaseSurface = OpenMaya.MObject()
	inputBaseMesh = OpenMaya.MObject()

	vectorTolerance = OpenMaya.MObject()

	offsetU = OpenMaya.MObject()
	offsetV = OpenMaya.MObject()
	offsetNormal = OpenMaya.MObject()

	rotateCenterU = OpenMaya.MObject()
	rotateCenterV = OpenMaya.MObject()
	rotate = OpenMaya.MObject()
	scaleU = OpenMaya.MObject()
	scaleV = OpenMaya.MObject()
	scaleNormal = OpenMaya.MObject()

	def __init__(self):
		OpenMayaMPx.MPxDeformerNode.__init__(self)

	def __del__(self):
		pass

	def deform(self, dataBlock, geoIterator, matrix, geometryIndex):

		#
		# make sure the various geos are connected
		#

		inputSurface = dataBlock.inputValue(uvSlider.inputSurface).asNurbsSurface()
		if inputSurface.isNull():
			return True

		inputBaseSurface = dataBlock.inputValue(uvSlider.inputBaseSurface).asNurbsSurface()
		if inputBaseSurface.isNull():
			return True

		inputBaseMesh = dataBlock.inputValue(uvSlider.inputBaseMesh).asMesh()
		if inputBaseMesh.isNull():
			return True

		#
		# get all the node attribute values
		#

		envelope = kEnvelope
		envelopeValue = dataBlock.inputValue(envelope).asFloat()

		vectorTolerance = dataBlock.inputValue(uvSlider.vectorTolerance).asFloat()

		offsetU = dataBlock.inputValue(uvSlider.offsetU).asFloat()
		offsetV = dataBlock.inputValue(uvSlider.offsetV).asFloat()
		offsetNormal = dataBlock.inputValue(uvSlider.offsetNormal).asFloat()

		rotateCenterU = dataBlock.inputValue(uvSlider.rotateCenterU).asFloat()
		rotateCenterV = dataBlock.inputValue(uvSlider.rotateCenterV).asFloat()
		rotate = dataBlock.inputValue(uvSlider.rotate).asFloat()
		scaleU = dataBlock.inputValue(uvSlider.scaleU).asFloat()
		scaleV = dataBlock.inputValue(uvSlider.scaleV).asFloat()
		scaleNormal = dataBlock.inputValue(uvSlider.scaleNormal).asFloat()

		fnInputSurface = OpenMaya.MFnNurbsSurface(inputSurface)
		fnInputBaseSurface = OpenMaya.MFnNurbsSurface(inputBaseSurface)
		fnInputBaseMesh = OpenMaya.MFnMesh(inputBaseMesh)

		#
		# define u v attributes
		#

		uScriptUtil = OpenMaya.MScriptUtil()
		uScriptUtil.createFromDouble(0.0)
		uPtr = uScriptUtil.asDoublePtr()

		vScriptUtil = OpenMaya.MScriptUtil()
		vScriptUtil.createFromDouble(0.0)
		vPtr = vScriptUtil.asDoublePtr()

		#
		# get min max params of inputSurface
		#

		uMinScriptUtil = OpenMaya.MScriptUtil()
		uMinScriptUtil.createFromDouble(0.0)
		uMinPtr = uMinScriptUtil.asDoublePtr()

		uMaxScriptUtil = OpenMaya.MScriptUtil()
		uMaxScriptUtil.createFromDouble(0.0)
		uMaxPtr = uMaxScriptUtil.asDoublePtr()

		vMinScriptUtil = OpenMaya.MScriptUtil()
		vMinScriptUtil.createFromDouble(0.0)
		vMinPtr = vMinScriptUtil.asDoublePtr()

		vMaxScriptUtil = OpenMaya.MScriptUtil()
		vMaxScriptUtil.createFromDouble(0.0)
		vMaxPtr = vMaxScriptUtil.asDoublePtr()

		fnInputSurface.getKnotDomain(uMinPtr, uMaxPtr, vMinPtr, vMaxPtr)
		formUType = fnInputSurface.formInU()
		formVType = fnInputSurface.formInV()
		#print(formUType,formVType)

		uMin = uMinScriptUtil.getDouble(uMinPtr)
		uMax = uMaxScriptUtil.getDouble(uMaxPtr)
		vMin = vMinScriptUtil.getDouble(vMinPtr)
		vMax = vMaxScriptUtil.getDouble(vMaxPtr)

		pointArray = OpenMaya.MPointArray()

		while( not geoIterator.isDone()):

			weight = self.weightValue(dataBlock, geometryIndex, geoIterator.index())

			index = geoIterator.index()

			###################################################################
			#
			# Get the Data from the Base Geo
			#
			###################################################################

			meshPoint = OpenMaya.MPoint()
			fnInputBaseMesh.getPoint(index, meshPoint, OpenMaya.MSpace.kWorld)
			closestPoint = fnInputBaseSurface.closestPoint(meshPoint)
			fnInputBaseSurface.getParamAtPoint(closestPoint, uPtr, vPtr)

			baseU = uScriptUtil.getDouble(uPtr)
			baseV = vScriptUtil.getDouble(vPtr)

			meshVector = OpenMaya.MVector(meshPoint.x-closestPoint.x, meshPoint.y-closestPoint.y, meshPoint.z-closestPoint.z)
			normalVector = fnInputBaseSurface.normal(baseU, baseV)
			angleRad = normalVector.angle(meshVector)
			angleFn = OpenMaya.MAngle(angleRad, OpenMaya.MAngle.kRadians)
			angle = angleFn.asDegrees()

			calculatePoint = True
			normalDirection = 1.0

			###################################################################
			#
			# Check if base vectors are parallel
			#
			###################################################################

			meshLength = meshVector.length()
			normalLength = normalVector.length()

			if angle > 180.0-vectorTolerance and angle < 180.0+vectorTolerance:
				normalDirection = -1.0

			pointPosition = geoIterator.position()

			###################################################################
			#
			# Calculate the point
			#
			###################################################################

			if calculatePoint:

				normalPercent = 0.0

				if meshLength > 0.0:
					normalPercent = meshLength/normalLength

				normalPercent = (normalPercent*normalDirection)+offsetNormal

				vectorU = baseU-rotateCenterU
				vectorV = baseV-rotateCenterV

				vectorPoint = OpenMaya.MVector( vectorU, vectorV, 0.0 )
				rotateVector = vectorPoint.rotateBy( OpenMaya.MVector.kZaxis, rotate )
				vectorURotate = rotateVector[0] * scaleU
				vectorVRotate = rotateVector[1] * scaleV

				newU = rotateCenterU + vectorURotate + offsetU
				newV = rotateCenterV + vectorVRotate + offsetV

				if formUType == 1:
					if newU < uMin:
						newU = uMin
					elif newU > uMax:
						newU = uMax
				else:
					multU = math.ceil(math.fabs(newU)/uMax)

					if newU < uMin:
						adjustedU = uMax-(math.fabs(newU)-(uMax*multU))
						newU = adjustedU
					elif newU > uMax:
						adjustedU = uMin+(math.fabs(newU)-(uMax*multU))
						newU = adjustedU

				if formVType == 1:
					if newV < vMin:
						newV = vMin
					elif newV > vMax:
						newV = vMax
				else:
					multV = math.floor(math.fabs(newV)/vMax)

					if newV < vMin:
						adjustedV = vMax-(math.fabs(newV)-(vMax*multV))
						newV = adjustedV
					elif newV > vMax:
						adjustedV = vMin+(math.fabs(newV)-(vMax*multV))
						newV = adjustedV

				newParamPoint = OpenMaya.MPoint()
				fnInputSurface.getPointAtParam(newU, newV, newParamPoint, OpenMaya.MSpace.kWorld)
				newNormalVector = fnInputSurface.normal(newU, newV, OpenMaya.MSpace.kWorld)

				endPoint = OpenMaya.MPoint()
				endPoint.x = newParamPoint.x + ( newNormalVector[0] * normalPercent * scaleNormal )
				endPoint.y = newParamPoint.y + ( newNormalVector[1] * normalPercent * scaleNormal )
				endPoint.z = newParamPoint.z + ( newNormalVector[2] * normalPercent * scaleNormal )

				delta = OpenMaya.MPoint()
				delta.x = (endPoint.x - pointPosition.x) * weight * envelopeValue
				delta.y = (endPoint.y - pointPosition.y) * weight * envelopeValue
				delta.z = (endPoint.z - pointPosition.z) * weight * envelopeValue

				newPoint = OpenMaya.MPoint()
				newPoint.x  = pointPosition.x + delta.x
				newPoint.y  = pointPosition.y + delta.y
				newPoint.z  = pointPosition.z + delta.z

				pointArray.append(newPoint)
			else:
				pointArray.append(pointPosition)

			geoIterator.next()

		geoIterator.setAllPositions(pointArray)


def deformerCreator():
	nodePtr = OpenMayaMPx.asMPxPtr(uvSlider())
	return nodePtr


def nodeInitializer():

	mFnAttr = OpenMaya.MFnNumericAttribute()
	mFnCAttr = OpenMaya.MFnCompoundAttribute()
	mFnTAttr = OpenMaya.MFnTypedAttribute()

	#input attrs
	uvSlider.inputSurface = mFnTAttr.create("inputSurface", "inputSurface", OpenMaya.MFnData.kNurbsSurface)
	uvSlider.inputBaseSurface = mFnTAttr.create("inputBaseSurface", "inputBaseSurface", OpenMaya.MFnData.kNurbsSurface)
	uvSlider.inputBaseMesh = mFnTAttr.create("inputBaseMesh", "inputBaseMesh", OpenMaya.MFnData.kMesh)
	uvSlider.addAttribute(uvSlider.inputSurface)
	uvSlider.addAttribute(uvSlider.inputBaseSurface)
	uvSlider.addAttribute(uvSlider.inputBaseMesh)

	uvSlider.vectorTolerance = mFnAttr.create("vectorTolerance", "vectorTolerance", OpenMaya.MFnNumericData.kFloat, 0.0001)
	uvSlider.addAttribute(uvSlider.vectorTolerance)

	uvSlider.offsetU = mFnAttr.create("offsetU", "offsetU", OpenMaya.MFnNumericData.kFloat, 0.0)
	uvSlider.offsetV = mFnAttr.create("offsetV", "offsetV", OpenMaya.MFnNumericData.kFloat, 0.0)
	uvSlider.offsetNormal = mFnAttr.create("offsetNormal", "offsetNormal", OpenMaya.MFnNumericData.kFloat, 0.0)
	uvSlider.addAttribute(uvSlider.offsetU)
	uvSlider.addAttribute(uvSlider.offsetV)
	uvSlider.addAttribute(uvSlider.offsetNormal)

	uvSlider.rotateCenterU = mFnAttr.create("rotateCenterU", "rotateCenterU", OpenMaya.MFnNumericData.kFloat, 0.0)
	uvSlider.rotateCenterV = mFnAttr.create("rotateCenterV", "rotateCenterV", OpenMaya.MFnNumericData.kFloat, 0.0)
	uvSlider.rotate = mFnAttr.create("rotate","rotate", OpenMaya.MFnNumericData.kFloat, 0.0)
	uvSlider.scaleU = mFnAttr.create("scaleU","scaleU", OpenMaya.MFnNumericData.kFloat, 1.0)
	uvSlider.scaleV = mFnAttr.create("scaleV","scaleV", OpenMaya.MFnNumericData.kFloat, 1.0)
	uvSlider.scaleNormal = mFnAttr.create("scaleNormal", "scaleNormal", OpenMaya.MFnNumericData.kFloat, 1.0)

	uvSlider.addAttribute(uvSlider.rotateCenterU)
	uvSlider.addAttribute(uvSlider.rotateCenterV)
	uvSlider.addAttribute(uvSlider.rotate)
	uvSlider.addAttribute(uvSlider.scaleU)
	uvSlider.addAttribute(uvSlider.scaleV)
	uvSlider.addAttribute(uvSlider.scaleNormal)

	#output attr
	uvSlider.attributeAffects( uvSlider.inputSurface, kOutputGeom )
	uvSlider.attributeAffects( uvSlider.inputBaseSurface, kOutputGeom )
	uvSlider.attributeAffects( uvSlider.inputBaseMesh, kOutputGeom )

	uvSlider.attributeAffects( uvSlider.vectorTolerance, kOutputGeom )

	uvSlider.attributeAffects( uvSlider.offsetU, kOutputGeom )
	uvSlider.attributeAffects( uvSlider.offsetV, kOutputGeom )
	uvSlider.attributeAffects( uvSlider.offsetNormal, kOutputGeom )

	uvSlider.attributeAffects( uvSlider.rotateCenterU, kOutputGeom )
	uvSlider.attributeAffects( uvSlider.rotateCenterV, kOutputGeom )
	uvSlider.attributeAffects( uvSlider.rotate, kOutputGeom )
	uvSlider.attributeAffects( uvSlider.scaleU, kOutputGeom )
	uvSlider.attributeAffects( uvSlider.scaleV, kOutputGeom )
	uvSlider.attributeAffects( uvSlider.scaleNormal, kOutputGeom )

	cmds.makePaintable('uvSlider', 'weights', attrType='multiFloat', shapeMode='deformer')


def initializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject, "Ryan Roberts", "1.0")
	try:
		mplugin.registerNode(nodeName, nodeId, deformerCreator, nodeInitializer, OpenMayaMPx.MPxNode.kDeformerNode)
	except:
		sys.stderr.write("Failed to register node: %s" % nodeName)
		raise


def uninitializePlugin(mobject):
	mplugin = OpenMayaMPx.MFnPlugin(mobject)
	try:
		mplugin.deregisterNode(nodeId)
	except:
		sys.stderr.write("Failed to deregister node: %s" % nodeName)
		raise
	