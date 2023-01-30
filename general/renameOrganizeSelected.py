# Original Author: Ryan Roberts
# ryanagogo@yahoo.com
# First published November 7 2014
# http://artofrigging.com/rename-joints-in-selected-joint-chains/

import maya.cmds as cmds
import math
import webbrowser
import __main__

#setup global variables in main maya scope
if not hasattr(__main__,'rroPrefix'):
	__main__.rroPrefix = []
if not hasattr(__main__,'rroGroupIndex'):
	__main__.rroGroupIndex = []
if not hasattr(__main__,'rroBody'):
	__main__.rroBody = []
if not hasattr(__main__,'rroItemIndex'):
	__main__.rroItemIndex = []
if not hasattr(__main__,'rroSuffix'):
	__main__.rroSuffix = []

if not hasattr(__main__,'rroSearch'):
	__main__.rroSearch = []
if not hasattr(__main__,'rroReplace'):
	__main__.rroReplace = []

if not hasattr(__main__,'rroUIFrameOpenCloseStates'):
	__main__.rroUIFrameOpenCloseStates = {}
	__main__.rroUIFrameOpenCloseStates['rename'] = False
	__main__.rroUIFrameOpenCloseStates['searchReplace'] = True
	__main__.rroUIFrameOpenCloseStates['reorder'] = True
	__main__.rroUIFrameOpenCloseStates['group'] = True


class Rename:
	def __init__( self ):
		pass

	initialGroupIndex = 0
	initialItemIndex = 0
	groupIndexType = 'number'
	groupLetters = ''
	groupPadding = ''
	groupCustomList = []
	itemIndexType = 'number'
	itemLetters = ''
	itemPadding = ''
	itemCustomList = []
	letterList = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']

	def getGroupIndex(self,index):
		self.groupLetters = ''

		if self.groupIndexType == 'none':
			return ''
		elif self.groupIndexType == 'custom':
			customString = ''
			customLength = len( self.groupCustomList )

			if index < customLength:
				customString = self.groupCustomList[index]
			else:
				customString = str(index+1)

			return customString
		elif self.groupIndexType == 'number':
			paddingCharacters = len( self.groupPadding )
			indexCharacters = len( str(index) )
			diff = paddingCharacters-indexCharacters
			pad = ''
			if diff > 0:
				for i in range(diff):
					pad = pad+'0'

			return pad+str(index)
		else:
			self.convertToGroupLetters( index )
			self.groupLetters = self.groupLetters[::-1]
			if self.groupIndexType == 'lowerCase':
				return self.groupLetters.lower()
			elif self.groupIndexType == 'upperCase':
				return self.groupLetters.upper()

	def getItemIndex(self,index):
		self.itemLetters = ''

		if self.itemIndexType == 'none':
			return ''
		elif self.itemIndexType == 'custom':
			customString = ''
			customLength = len( self.itemCustomList )

			if index < customLength:
				customString = self.itemCustomList[index]
			else:
				customString = str(index+1)

			return customString
		elif self.itemIndexType == 'number':
			paddingCharacters = len( self.itemPadding )
			indexCharacters = len( str(index) )
			diff = paddingCharacters-indexCharacters
			pad = ''
			if diff > 0:
				for i in range(diff):
					pad = pad+'0'

			return pad+str(index)
		else:
			self.convertToItemLetters( index )
			self.itemLetters = self.itemLetters[::-1]
			if self.itemIndexType == 'lowerCase':
				return self.itemLetters.lower()
			elif self.itemIndexType == 'upperCase':
				return self.itemLetters.upper()

	def convertToItemLetters( self, result ):
		baseNumber = len(self.letterList)
		x = int( math.floor(float(result)/baseNumber) )
		mult = x*baseNumber
		diff = result-mult
		letter = self.letterList[diff-1]
		self.itemLetters = self.itemLetters+letter

		if diff == 0:
			x = x-1

		if x > 0:
			newResult = x
			self.convertToItemLetters( newResult )

	def convertToGroupLetters( self, result ):
		baseNumber = len(self.letterList)
		x = int( math.floor(float(result)/baseNumber) )
		mult = x*baseNumber
		diff = result-mult
		letter = self.letterList[diff-1]
		self.groupLetters = self.groupLetters+letter

		if diff == 0:
			x = x-1

		if x > 0:
			newResult = x
			self.convertToGroupLetters( newResult )

	def setInitialGroupIndex(self):
		indexString = cmds.textField( 'groupIndexTextField', query=True, tx=True )

		if indexString == '':
			self.initialGroupIndex = -1
			self.groupIndexType = 'none'
		else:
			self.groupCustomList = indexString.split(',')
			if len(self.groupCustomList) > 1:
				self.initialGroupIndex = 0
				self.groupIndexType = 'custom'
			else:
				if indexString.isdigit():
					indexStringCharacters = len(indexString)
					self.initialGroupIndex = int(indexString)

					self.groupPadding = ''
					if self.groupPadding > 0:
						for i in range(indexStringCharacters):
							self.groupPadding = self.groupPadding+'0'
					self.groupIndexType = 'number'

				elif indexString.isalpha():
					baseNumber = len(self.letterList)
					tempList = list(indexString)
					tempList.reverse()
					finalResult = 0

					for x,item in enumerate( tempList ):
						mult = int( math.pow(baseNumber,x) )
						currentIndex = self.letterList.index(item.lower())+1
						result = currentIndex*mult
						finalResult = finalResult+result

					self.initialGroupIndex = finalResult

					if indexString.isupper():
						self.groupIndexType = 'upperCase'
					else:
						self.groupIndexType = 'lowerCase'

	def setInitialItemIndex(self):
		indexString = cmds.textField( 'itemIndexTextField', query=True, tx=True )

		if indexString == '':
			initialIndex = -1
			self.itemIndexType = 'none'
		else:
			self.itemCustomList = indexString.split(',')
			if len(self.itemCustomList) > 1:
				self.initialItemIndex = 0
				self.itemIndexType = 'custom'
			else:
				if indexString.isdigit():
					indexStringCharacters = len(indexString)
					self.initialItemIndex = int(indexString)

					self.itemPadding = ''
					if self.itemPadding > 0:
						for i in range(indexStringCharacters):
							self.itemPadding = self.itemPadding+'0'
					self.itemIndexType = 'number'

				elif indexString.isalpha():
					baseNumber = len(self.letterList)
					tempList = list(indexString)
					tempList.reverse()
					finalResult = 0

					for x,item in enumerate( tempList ):
						mult = int( math.pow(baseNumber,x) )
						currentIndex = self.letterList.index(item.lower())+1
						result = currentIndex*mult
						finalResult = finalResult+result

					self.initialItemIndex = finalResult

					if indexString.isupper():
						self.itemIndexType = 'upperCase'
					else:
						self.itemIndexType = 'lowerCase'

	def renameGroup(self,*args):
		ui.saveRenameText()
		self.setInitialGroupIndex()
		self.setInitialItemIndex()

		groupIndex = self.initialGroupIndex
		switchIndex = cmds.checkBox( 'switchIndexesCheckBox', query=True, v=True )

		prefix = cmds.textField( 'prefixTextField', query=True, tx=True )
		body = cmds.textField( 'bodyTextField', query=True, tx=True )
		suffix = cmds.textField( 'suffixTextField', query=True, tx=True )

		for group in cmds.ls( sl=True ):
			itemIndex = self.initialItemIndex
			groupItems = cmds.listRelatives( group, children=True, pa=True )

			#give items a temp name, to help lessen chance of new name already existing
			#won't prevent it with items that exist outside of the selection
			for index,item in enumerate(groupItems):
				splitName = item.split('|')[-1]
				cmds.rename( item, splitName+'XXX'+str(index) )

			#get the group items again to pick up the new names
			groupItems = cmds.listRelatives( group, children=True, pa=True )

			for item in groupItems:
				groupIndexString = self.getGroupIndex(groupIndex)
				itemIndexString = self.getItemIndex(itemIndex)

				newName = prefix+groupIndexString+body+itemIndexString+suffix
				if switchIndex is True:
					newName = prefix+itemIndexString+body+groupIndexString+suffix

				cmds.rename( item, newName )

				itemIndex = itemIndex+1

			groupIndex = groupIndex+1

	def renameSelected(self,*args):
		ui.saveRenameText()
		self.setInitialGroupIndex()
		self.setInitialItemIndex()

		itemIndex = self.initialItemIndex
		groupIndex = self.initialGroupIndex
		switchIndex = cmds.checkBox( 'switchIndexesCheckBox', query=True, v=True )

		prefix = cmds.textField( 'prefixTextField', query=True, tx=True )
		body = cmds.textField( 'bodyTextField', query=True, tx=True )
		suffix = cmds.textField( 'suffixTextField', query=True, tx=True )

		groupIndexString = self.getGroupIndex(groupIndex)

		#give items a temp name, to help lessen chance of new name already existing
		#won't prevent it with items that exist outside of the selection
		for index,item in enumerate(cmds.ls( sl=True )):
			splitName = item.split('|')[-1]
			cmds.rename( item, splitName+'XXX'+str(index) )

		for item in cmds.ls( sl=True ):
			itemIndexString = self.getItemIndex(itemIndex)

			newName = prefix+groupIndexString+body+itemIndexString+suffix
			if switchIndex is True:
				newName = prefix+itemIndexString+body+groupIndexString+suffix

			cmds.rename( item, newName )

			itemIndex = itemIndex+1

	def renameSelectedChains(self,*args):
		ui.saveRenameText()
		self.setInitialGroupIndex()
		self.setInitialItemIndex()

		self.itemIndex = self.initialItemIndex
		self.groupIndex = self.initialGroupIndex
		self.switchIndex = cmds.checkBox( 'switchIndexesCheckBox', query=True, v=True )

		self.prefix = cmds.textField( 'prefixTextField', query=True, tx=True )
		self.body = cmds.textField( 'bodyTextField', query=True, tx=True )
		self.suffix = cmds.textField( 'suffixTextField', query=True, tx=True )

		for chainCountIndex,selectedJoint in enumerate(cmds.ls( sl=True )):
			self.renameChain( selectedJoint )
			self.groupIndex = self.groupIndex+1

	def renameChain( self, parentJoint ):
		prefix = self.prefix
		body = self.body
		suffix = self.suffix

		if parentJoint is not False and prefix is not False:
			groupIndexString = self.getGroupIndex(self.groupIndex)
			itemIndexString = self.getItemIndex(self.itemIndex)

			newName = prefix+groupIndexString+body+itemIndexString+suffix

			if self.switchIndex is True:
				newName = prefix+itemIndexString+body+groupIndexString+suffix

			newName = cmds.rename( parentJoint, newName )

			childJoint = cmds.listRelatives( newName, c=True, path=True )

			self.itemIndex = self.itemIndex+1
			if childJoint is not None:
				self.renameChain( childJoint[0] )

	def addSuffixToSelected(self,*args):
		ui.saveAddSuffixText()
		suffix = cmds.textField( 'suffixTextField', query=True, tx=True )
		for item in cmds.ls( sl=True ):
			cmds.rename( item, item+suffix )

	def addSuffixToGroup(self,*args):
		ui.saveAddSuffixText()
		suffix = cmds.textField( 'suffixTextField', query=True, tx=True )
		for group in cmds.ls( sl=True ):
			groupItems = cmds.listRelatives( group, children=True, pa=True )

			for item in groupItems:
				cmds.rename( item, item+suffix )

	def addSuffixToChains(self,*args):
		ui.saveAddSuffixText()
		self.suffix = cmds.textField( 'addPrefixSuffixTextField', query=True, tx=True )

		for selectedJoint in cmds.ls( sl=True ):
			self.addSuffixToChain( selectedJoint )

	def addSuffixToChain( self, parentJoint ):
		suffix = self.suffix

		if parentJoint is not False and suffix is not False:
			childJoint = cmds.listRelatives( parentJoint, c=True, path=True )
			if childJoint is not None:
				self.addSuffixToChain( childJoint[0] )

			oldName = parentJoint
			splitName = oldName.split('|')[-1]
			newName = splitName+suffix
			cmds.rename( parentJoint, newName )

	def addPrefixToSelected(self,*args):
		ui.saveAddPrefixText()
		prefix = cmds.textField( 'prefixTextField', query=True, tx=True )
		for item in cmds.ls( sl=True ):
			cmds.rename( item, prefix+item )

	def addPrefixToGroup(self,*args):
		ui.saveAddPrefixText()
		prefix = cmds.textField( 'prefixTextField', query=True, tx=True )
		for group in cmds.ls( sl=True ):
			groupItems = cmds.listRelatives( group, children=True, pa=True )
			for item in groupItems:
				cmds.rename( item, prefix+item )

	def addPrefixToChains(self,*args):
		ui.saveAddPrefixText()
		self.prefix = cmds.textField( 'addPrefixSuffixTextField', query=True, tx=True )

		for selectedJoint in cmds.ls( sl=True ):
			self.addPrefixToChain( selectedJoint )

	def addPrefixToChain( self, parentJoint ):
		prefix = self.prefix

		if parentJoint is not False and prefix is not False:
			childJoint = cmds.listRelatives( parentJoint, c=True, path=True )
			if childJoint is not None:
				self.addPrefixToChain( childJoint[0] )

			oldName = parentJoint
			splitName = oldName.split('|')[-1]
			newName = prefix+splitName
			cmds.rename( parentJoint, newName )

	def searchReplaceSelected(self,*args):
		ui.saveSearchReplaceText()
		search = cmds.textField( 'searchTextField', query=True, tx=True )
		replace = cmds.textField( 'replaceTextField', query=True, tx=True )

		for item in cmds.ls( sl=True ):
			oldName = item
			splitName = oldName.split('|')[-1]
			newName = splitName.replace( search, replace )
			newName = cmds.rename( item, newName )
			print ( oldName+' -> '+newName )

	def searchReplaceGroupChildren(self,*args):
		ui.saveSearchReplaceText()
		search = cmds.textField( 'searchTextField', query=True, tx=True )
		replace = cmds.textField( 'replaceTextField', query=True, tx=True )
		for group in cmds.ls( sl=True ):
			groupItems = cmds.listRelatives( group, children=True, pa=True )
			for item in groupItems:
				oldName = item
				splitName = oldName.split('|')[-1]
				newName = splitName.replace( search, replace )
				newName = cmds.rename( item, newName )
				print ( oldName+' -> '+newName )

	def searchReplaceSelectedChains(self,*args):
		ui.saveSearchReplaceText()
		self.search = cmds.textField( 'searchTextField', query=True, tx=True )
		self.replace = cmds.textField( 'replaceTextField', query=True, tx=True )

		for index,parentJoint in enumerate( cmds.ls( sl=True ) ):
			self.searchReplaceChain( parentJoint )

	def searchReplaceChain( self, parentJoint ):
		search = self.search
		replace = self.replace

		if parentJoint is not False and search is not False and replace is not False:
			childJoint = cmds.listRelatives( parentJoint, c=True, path=True )
			if childJoint is not None:
				self.searchReplaceChain( childJoint[0] )

			oldName = parentJoint
			splitName = oldName.split('|')[-1]
			newName = splitName.replace( search, replace )
			cmds.rename( parentJoint, newName )
			print ( oldName+' -> '+newName )

class Reorder:
	def __init__( self ):
		pass

	def moveTop(self,*args):
		selected = cmds.ls( sl=True )
		cmds.reorder( selected, front=True )

	def moveUp(self,*args):
		selected = cmds.ls( sl=True )
		cmds.reorder( selected, relative=-1 )

	def moveDown(self,*args):
		selected = cmds.ls( sl=True )
		cmds.reorder( selected, relative=1 )

	def moveBottom(self,*args):
		selected = cmds.ls( sl=True )
		cmds.reorder( selected, back=True )

	def sortSelected(self,type='asc'):
		selected = cmds.ls( sl=True )
		selectedDictionary = {}
		for item in selected:
			key = item.split('|')[-1]
			selectedDictionary[key] = item

		selectedKeys = selectedDictionary.keys()
		if type == 'asc':
			selectedKeys.sort()
		elif type == 'desc':
			selectedKeys.sort(reverse=True)
		else:
			return None

		sortSelected = []
		for key in selectedKeys:
			sortSelected.append(selectedDictionary[key])

		parentResult = cmds.listRelatives( selected[0], parent=True )

		if parentResult is not None:
			parent = parentResult[0]
			children = cmds.listRelatives( parent, children=True, pa=True )
			sortIndex = 0

			currentIndexex = []
			for index,item in enumerate(children):
				if item in selected:
					currentIndexex.append(index)
					sortIndex = sortIndex+1

			for index, currentIndex in enumerate(currentIndexex):
				children[currentIndex] = sortSelected[index]

			for item in children:
				cmds.reorder( item, back=True )

			cmds.select( sortSelected )
		else:
			cmds.warning( 'Selected objects are parented to the World, they need to be children of a transform' )

	def selectedAsc(self,*args):
		self.sortSelected('asc')

	def selectedDesc(self,*args):
		self.sortSelected('desc')

	def groupChildren(self,type='asc'):
		groups = cmds.ls( sl=True )
		for group in groups:
			groupChildren = cmds.listRelatives(group, children=True, pa=True)

			childrenDictionary = {}
			for item in groupChildren:
				key = item.split('|')[-1]
				childrenDictionary[key] = item

			childrenKeys = childrenDictionary.keys()
			if type == 'asc':
				childrenKeys.sort()
			elif type == 'desc':
				childrenKeys.sort(reverse=True)
			else:
				return None

			sortChildren = []
			for key in childrenKeys:
				sortChildren.append(childrenDictionary[key])

			for item in sortChildren:
				cmds.reorder( item, back=True )

	def groupChildrenAsc(self,*args):
		self.groupChildren('asc')

	def groupChildrenDesc(self,*args):
		self.groupChildren('desc')

	def reverseSelected(self,*args):
		selected = cmds.ls( sl=True )
		reverseSelected = cmds.ls( sl=True )

		parentResult = cmds.listRelatives( selected[0], parent=True )

		if parentResult is not None:
			parent = parentResult[0]
			children = cmds.listRelatives( parent, children=True, pa=True )

			reverseSelected.reverse()
			reverseIndex = 0

			numberOfSelected = len(selected)

			for item in children:
				if reverseIndex < numberOfSelected and item == selected[reverseIndex]:
					cmds.reorder( reverseSelected[reverseIndex], back=True )
					reverseIndex = reverseIndex+1
				else:
					cmds.reorder( item, back=True )

			cmds.select( reverseSelected )
		else:
			cmds.warning( 'Selected objects are parented to the World, they need to be children of a transform' )

	def reverseGroupChildren(self,*args):
		selected = cmds.ls( sl=True )
		for group in selected:
			children = cmds.listRelatives( group, children=True, pa=True )
			children.reverse()
			for item in children:
				cmds.reorder( item, back=True )

class UI:
	def __init__( self ):
		pass

	height = 30

	def openHelpPage(*args):
		webbrowser.open('http://artofrigging.com/rename-and-organize-ui/',new=2)

	def changeFrameState(self):
		for index in ['rename','searchReplace','reorder']:
			state = cmds.frameLayout( index+'FrameLayout', query=True, cl=True )
			__main__.rroUIFrameOpenCloseStates[index] = state


	def create(self):
		windowName = 'renameAndOrganizeUI'

		if cmds.window( windowName, exists=True ):
			cmds.deleteUI( windowName, wnd=True )

		#create window
		window = cmds.window( windowName, title='Ryan Roberts: Rename and Organize v1.2', mb=True, mbv=True )

		mainMenu = cmds.menu( 'mainMenu', label='Help' )
		cmds.menuItem( label='Clear Fields', command=self.clearHistory )
		cmds.menuItem( label='Online Document', command=self.openHelpPage )

		#layout
		mainFormLayout = cmds.formLayout( 'renameOrganizeMainFormLayout', parent=window )
		renameFrameLayout = cmds.frameLayout( 'renameFrameLayout', label='Rename', cll=True, mh=20, mw=20, cc=self.changeFrameState, ec=self.changeFrameState, parent=mainFormLayout )
		searchReplaceFrameLayout = cmds.frameLayout( 'searchReplaceFrameLayout', label='Search and Replace', cll=True, mh=20, mw=20, cc=self.changeFrameState, ec=self.changeFrameState, parent=mainFormLayout )
		reorderFrameLayout = cmds.frameLayout( 'reorderFrameLayout', label='Reorder', cll=True, mh=20, mw=20, cc=self.changeFrameState, ec=self.changeFrameState, parent=mainFormLayout )

		attachPositionData = [
			[renameFrameLayout,'top',0,0],
			[renameFrameLayout,'left',0,0],
			[renameFrameLayout,'right',0,100],

			[searchReplaceFrameLayout,'left',0,0],
			[searchReplaceFrameLayout,'right',0,100],

			[reorderFrameLayout,'left',0,0],
			[reorderFrameLayout,'right',0,100]
		]

		attachControlData = [
			[searchReplaceFrameLayout,'top',0,renameFrameLayout],
			[reorderFrameLayout,'top',0,searchReplaceFrameLayout]
		]

		cmds.formLayout( mainFormLayout, edit=True, ap=attachPositionData, ac=attachControlData )

		renameFormLayout = cmds.formLayout( 'renameFormLayout', parent=renameFrameLayout )
		searchReplaceFormLayout = cmds.formLayout( 'searchReplaceFormLayout', parent=searchReplaceFrameLayout )
		reorderFormLayout = cmds.formLayout( 'reorderFormLayout', parent=reorderFrameLayout )

		################################################################
		#
		#   RENAME SELECTED / CHILDREN
		#
		################################################################

		layout = renameFormLayout

		prefixTextTitle = cmds.text( 'prefixText', label='Prefix', h=self.height, parent=layout )
		prefixTextField = cmds.textField( 'prefixTextField', h=self.height, parent=layout )
		cmds.popupMenu( 'prefixTextPopupMenu' )

		groupIndexTitle = cmds.text( 'groupIndexText', h=self.height, label='Grp Index', parent=layout )
		groupIndexField = cmds.textField( 'groupIndexTextField', h=self.height, text='0', parent=layout )
		cmds.popupMenu( 'groupIndexTextPopupMenu' )

		bodyTitle = cmds.text( 'bodyText', label='Body', h=self.height, parent=layout )
		bodyField = cmds.textField( 'bodyTextField', text='', h=self.height, parent=layout )
		cmds.popupMenu( 'bodyTextPopupMenu' )

		itemIndexTitle = cmds.text( 'itemIndexText', h=self.height, label='Item Index', parent=layout )
		itemIndexField = cmds.textField( 'itemIndexTextField', text='0', h=self.height, parent=layout )
		cmds.popupMenu( 'itemIndexTextPopupMenu' )

		suffixTextTitle = cmds.text( 'suffixText', label='Suffix', h=self.height, parent=layout )
		suffixTextField = cmds.textField( 'suffixTextField', h=self.height, parent=layout )
		cmds.popupMenu( 'suffixTextPopupMenu' )

		switchIndexesCheckbox = cmds.checkBox( 'switchIndexesCheckBox', label='Switch Indexes', v=False, h=self.height, cc=self.switchIndexes, parent=layout )

		attachPositionData = [
			[prefixTextTitle,'top',0,0],
			[prefixTextTitle,'left',0,0],
			[prefixTextTitle,'right',0,15],

			[groupIndexTitle,'left',0,0],
			[groupIndexTitle,'right',0,15],

			[bodyTitle,'left',0,0],
			[bodyTitle,'right',0,15],

			[itemIndexTitle,'left',0,0],
			[itemIndexTitle,'right',0,15],

			[suffixTextTitle,'left',0,0],
			[suffixTextTitle,'right',0,15],

			[switchIndexesCheckbox,'left',0,0],
			[switchIndexesCheckbox,'right',0,33],
		]

		attachControlData = [
			[groupIndexTitle,'top',5,prefixTextTitle],
			[bodyTitle,'top',5,groupIndexTitle],
			[itemIndexTitle,'top',5,bodyTitle],
			[suffixTextTitle,'top',5,itemIndexTitle],
		    [switchIndexesCheckbox,'top',5,suffixTextField]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData, ac=attachControlData )

		attachPositionData = [
			[prefixTextField,'top',0,0],
			[prefixTextField,'left',0,15],
			[prefixTextField,'right',0,100],

			[groupIndexField,'left',0,15],
			[groupIndexField,'right',0,100],

			[bodyField,'left',0,15],
			[bodyField,'right',0,100],

			[itemIndexField,'left',0,15],
			[itemIndexField,'right',0,100],

			[suffixTextField,'left',0,15],
			[suffixTextField,'right',0,100]
		]

		attachControlData = [
			[groupIndexField,'top',5,prefixTextField],
			[bodyField,'top',5,groupIndexField],
			[itemIndexField,'top',5,bodyField],
			[suffixTextField,'top',5,itemIndexField]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData, ac=attachControlData )

		################################################################
		#
		#   RENAME and ADD PREFIX / SUFFIX
		#
		################################################################

		addPrefixTextTitle = cmds.text( label='Add Prefix', h=self.height, parent=layout )
		addPrefixSelectedButton = cmds.button( label='To Selected', h=self.height, command=rename.addPrefixToSelected, parent=layout )
		addPrefixGroupButton = cmds.button( label='To Children', h=self.height, command=rename.addPrefixToGroup, parent=layout )
		addPrefixChainsButton = cmds.button( label='To Chains', h=self.height, command=rename.addPrefixToChains, parent=layout )

		renameTextTitle = cmds.text( label='Rename', h=self.height, parent=layout )
		renameSelectedButton = cmds.button( label='Rename Selected', h=self.height, command=rename.renameSelected, parent=layout )
		renameGroupButton = cmds.button( label='Rename Children', h=self.height, command=rename.renameGroup, parent=layout )
		renameChainButton = cmds.button( label='Rename Chains', h=self.height, command=rename.renameSelectedChains, parent=layout )

		addSuffixTextTitle = cmds.text( label='Add Suffix', h=self.height, parent=layout )
		addSuffixSelectedButton = cmds.button( label='To Selected', h=self.height, command=rename.addSuffixToSelected, parent=layout )
		addSuffixGroupButton = cmds.button( label='To Children', h=self.height, command=rename.addSuffixToGroup, parent=layout )
		addSuffixChainsButton = cmds.button( label='To Chains', h=self.height, command=rename.addSuffixToChains, parent=layout )

		#add prefix column

		attachPositionData = [
			[addPrefixTextTitle,'left',0,0],
			[addPrefixTextTitle,'right',0,25],

			[addPrefixSelectedButton,'left',0,0],
			[addPrefixSelectedButton,'right',0,25],

			[addPrefixGroupButton,'left',0,0],
			[addPrefixGroupButton,'right',0,25],

			[addPrefixChainsButton,'left',0,0],
			[addPrefixChainsButton,'right',0,25]
		]

		attachControlData = [
			[addPrefixTextTitle,'top',5,switchIndexesCheckbox],
			[addPrefixSelectedButton,'top',5,addPrefixTextTitle],
			[addPrefixGroupButton,'top',5,addPrefixSelectedButton],
		    [addPrefixChainsButton,'top',5,addPrefixGroupButton]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData, ac=attachControlData )

		#rename column

		attachPositionData = [
			[renameTextTitle,'left',5,25],
			[renameTextTitle,'right',5,75],

			[renameSelectedButton,'left',5,25],
			[renameSelectedButton,'right',5,75],

			[renameGroupButton,'left',5,25],
			[renameGroupButton,'right',5,75],

			[renameChainButton,'left',5,25],
			[renameChainButton,'right',5,75]
		]

		attachControlData = [
			[renameTextTitle,'top',5,switchIndexesCheckbox],
			[renameSelectedButton,'top',5,renameTextTitle],
			[renameGroupButton,'top',5,renameSelectedButton],
		    [renameChainButton,'top',5,renameGroupButton]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData, ac=attachControlData )

		#add suffix column

		attachPositionData = [
			[addSuffixTextTitle,'left',0,75],
			[addSuffixTextTitle,'right',0,100],

			[addSuffixSelectedButton,'left',0,75],
			[addSuffixSelectedButton,'right',0,100],

			[addSuffixGroupButton,'left',0,75],
			[addSuffixGroupButton,'right',0,100],

			[addSuffixChainsButton,'left',0,75],
			[addSuffixChainsButton,'right',0,100]
		]

		attachControlData = [
			[addSuffixTextTitle,'top',5,switchIndexesCheckbox],
			[addSuffixSelectedButton,'top',5,addSuffixTextTitle],
			[addSuffixGroupButton,'top',5,addSuffixSelectedButton],
		    [addSuffixChainsButton,'top',5,addSuffixGroupButton]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData, ac=attachControlData )

		################################################################
		#
		#   SEARCH AND REPLACE
		#
		################################################################

		layout = searchReplaceFormLayout

		searchTextTitle = cmds.text( label='Search SubString', parent=layout )
		searchTextField = cmds.textField( 'searchTextField', h=self.height, parent=layout )
		cmds.popupMenu( 'searchTextPopupMenu' )

		replaceTextTitle = cmds.text( label='Replace Substring', parent=layout )
		replaceTextField = cmds.textField( 'replaceTextField', h=self.height, parent=layout )
		cmds.popupMenu( 'replaceTextPopupMenu' )

		searchAndReplaceSelectedButton = cmds.button( label='Search Replace Selected', h=self.height, command=rename.searchReplaceSelected, parent=layout )
		searchAndReplaceGroupChildrenButton = cmds.button( label='Search Replace Children', h=self.height, command=rename.searchReplaceGroupChildren, parent=layout )
		searchAndReplaceChainsChildrenButton = cmds.button( label='Search Replace Chains', h=self.height, command=rename.searchReplaceSelectedChains, parent=layout )

		attachPositionData = [
			[searchTextTitle,'top',0,0],
			[searchTextTitle,'left',0,15],
			[searchTextTitle,'right',0,50],

			[replaceTextTitle,'top',0,0],
			[replaceTextTitle,'left',0,50],
			[replaceTextTitle,'right',0,85]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData )

		attachPositionData = [
			[searchTextField,'left',0,15],
			[searchTextField,'right',0,50],

			[replaceTextField,'left',0,50],
			[replaceTextField,'right',0,85]
		]

		attachControlData = [
			[searchTextField,'top',10,searchTextTitle],
			[replaceTextField,'top',10,searchTextTitle]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData, ac=attachControlData )

		size = 27
		diff = (100 - (size*3))/2

		attachPositionData = [
			[searchAndReplaceSelectedButton,'left',0,diff],
			[searchAndReplaceSelectedButton,'right',0,diff+size],

			[searchAndReplaceGroupChildrenButton,'left',0,diff+size],
			[searchAndReplaceGroupChildrenButton,'right',0,diff+(size*2)],

			[searchAndReplaceChainsChildrenButton,'left',0,diff+(size*2)],
			[searchAndReplaceChainsChildrenButton,'right',0,diff+(size*3)]
		]

		attachControlData = [
			[searchAndReplaceSelectedButton,'top',10,searchTextField],
			[searchAndReplaceGroupChildrenButton,'top',10,searchTextField],
		    [searchAndReplaceChainsChildrenButton,'top',10,searchTextField]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData, ac=attachControlData )

		################################################################
		#
		#   REORDER
		#
		################################################################

		layout = reorderFormLayout

		moveSelectedTextTitle = cmds.text( label='Move Selected', parent=layout )
		moveTopButton = cmds.button( label='Top',command=reorder.moveTop, h=self.height, parent=layout )
		moveUpButton = cmds.button( label='Up',command=reorder.moveUp, h=self.height, parent=layout )
		moveDownButton = cmds.button( label='Down',command=reorder.moveDown, h=self.height, parent=layout )
		moveBottomButton = cmds.button( label='Bottom',command=reorder.moveBottom, h=self.height, parent=layout )

		attachPositionData = [
			[moveSelectedTextTitle,'top',0,0],
			[moveSelectedTextTitle,'left',0,0],
			[moveSelectedTextTitle,'right',10,20]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData )

		attachPositionData = [
			[moveTopButton,'left',0,0],
			[moveTopButton,'right',10,20],

			[moveUpButton,'left',0,0],
			[moveUpButton,'right',10,20],

			[moveDownButton,'left',0,0],
			[moveDownButton,'right',10,20],

			[moveBottomButton,'left',0,0],
			[moveBottomButton,'right',10,20]
		]

		attachControlData = [
			[moveTopButton,'top',10,moveSelectedTextTitle],
			[moveUpButton,'top',0,moveTopButton],
			[moveDownButton,'top',0,moveUpButton],
			[moveBottomButton,'top',0,moveDownButton]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData, ac=attachControlData )

		orderByTextTitle = cmds.text( label='Sort By Name', parent=layout )

		orderSelectedAscButton = cmds.button( label='Sort Selected Asc',command=reorder.selectedAsc, h=self.height, parent=layout )
		orderSelectedDescButton = cmds.button( label='Sort Selected Desc',command=reorder.selectedDesc, h=self.height, parent=layout )
		orderGroupChildrenAscButton = cmds.button( label='Sort Children Asc',command=reorder.groupChildrenAsc, h=self.height, parent=layout )
		orderGroupChildrenDescButton = cmds.button( label='Sort Children Desc',command=reorder.groupChildrenDesc, h=self.height, parent=layout )

		attachPositionData = [
			[orderByTextTitle,'top',0,0],
			[orderByTextTitle,'left',0,20],
			[orderByTextTitle,'right',0,70]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData )

		attachPositionData = [
			[orderSelectedAscButton,'left',0,20],
			[orderSelectedAscButton,'right',0,45],

			[orderSelectedDescButton,'left',0,45],
			[orderSelectedDescButton,'right',0,70],

			[orderGroupChildrenAscButton,'left',0,20],
			[orderGroupChildrenAscButton,'right',0,45],

			[orderGroupChildrenDescButton,'left',0,45],
			[orderGroupChildrenDescButton,'right',0,70]
		]

		attachControlData = [
			[orderSelectedAscButton,'top',10,orderByTextTitle],
			[orderSelectedDescButton,'top',10,orderByTextTitle],
			[orderGroupChildrenAscButton,'top',20,orderSelectedAscButton],
			[orderGroupChildrenDescButton,'top',20,orderSelectedAscButton]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData, ac=attachControlData )

		reverseOrderTextTitle = cmds.text( label='Reverse Order', parent=layout )
		reverseSelectedButton = cmds.button( label='Reverse Selected',command=reorder.reverseSelected, h=self.height, parent=layout )
		reverseGroupChildrenButton = cmds.button( label='Reverse Children',command=reorder.reverseGroupChildren, h=self.height, parent=layout )

		attachPositionData = [
			[reverseOrderTextTitle,'top',0,0],
			[reverseOrderTextTitle,'left',10,70],
			[reverseOrderTextTitle,'right',0,100]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData )

		attachPositionData = [
			[reverseSelectedButton,'left',10,70],
			[reverseSelectedButton,'right',0,100],

			[reverseGroupChildrenButton,'left',10,70],
			[reverseGroupChildrenButton,'right',0,100]
		]

		attachControlData = [
			[reverseSelectedButton,'top',10,reverseOrderTextTitle],
			[reverseGroupChildrenButton,'top',20,reverseSelectedButton]
		]

		cmds.formLayout( layout, edit=True, ap=attachPositionData, ac=attachControlData )

		self.initialize()

		cmds.showWindow( windowName )

	def initialize(self):
		if len(__main__.rroPrefix) > 0:
			cmds.textField( 'prefixTextField', edit=True, text=__main__.rroPrefix[len(__main__.rroPrefix)-1] )
		if len(__main__.rroGroupIndex) > 0:
			cmds.textField( 'groupIndexTextField', edit=True, text=__main__.rroGroupIndex[len(__main__.rroGroupIndex)-1] )
		if len(__main__.rroBody) > 0:
			cmds.textField( 'bodyTextField', edit=True, text=__main__.rroBody[len(__main__.rroBody)-1] )
		if len(__main__.rroItemIndex) > 0:
			cmds.textField( 'itemIndexTextField', edit=True, text=__main__.rroItemIndex[len(__main__.rroItemIndex)-1] )
		if len(__main__.rroSuffix) > 0:
			cmds.textField( 'suffixTextField', edit=True, text=__main__.rroSuffix[len(__main__.rroSuffix)-1] )

		if len(__main__.rroSearch) > 0:
			cmds.textField( 'searchTextField', edit=True, text=__main__.rroSearch[len(__main__.rroSearch)-1] )
		if len(__main__.rroReplace) > 0:
			cmds.textField( 'replaceTextField', edit=True, text=__main__.rroReplace[len(__main__.rroReplace)-1] )

		self.setFrameStates()
		self.setupPopupMenus()

	def setFrameStates(self):
		for index in ['rename','searchReplace','reorder']:
			state = __main__.rroUIFrameOpenCloseStates[index]
			cmds.frameLayout( index+'FrameLayout', edit=True, cl=state )

	def saveSearchReplaceText(self):
		search = cmds.textField( 'searchTextField', query=True, tx=True )
		replace = cmds.textField( 'replaceTextField', query=True, tx=True )

		if search in __main__.rroSearch:
			__main__.rroSearch.remove(search)
		if replace in __main__.rroReplace:
			__main__.rroReplace.remove(replace)

		__main__.rroSearch.append(search)
		__main__.rroReplace.append(replace)

		self.setupPopupMenus()

	def saveAddPrefixText(self):
		prefix = cmds.textField( 'prefixTextField', query=True, tx=True )

		if prefix in __main__.rroPrefix:
			__main__.rroPrefix.remove(prefix)

		__main__.rroPrefix.append(prefix)

		self.setupPopupMenus()

	def saveAddSuffixText(self):
		suffix = cmds.textField( 'suffixTextField', query=True, tx=True )

		if suffix in __main__.rroSuffix:
			__main__.rroSuffix.remove(suffix)

		__main__.rroSuffix.append(suffix)

		self.setupPopupMenus()

	def saveRenameText(self):
		prefix = cmds.textField( 'prefixTextField', query=True, tx=True )
		groupIndex = cmds.textField( 'groupIndexTextField', query=True, tx=True )
		body = cmds.textField( 'bodyTextField', query=True, tx=True )
		itemIndex = cmds.textField( 'itemIndexTextField', query=True, tx=True )
		suffix = cmds.textField( 'suffixTextField', query=True, tx=True )

		if prefix in __main__.rroPrefix:
			__main__.rroPrefix.remove(prefix)
		if groupIndex in __main__.rroGroupIndex:
			__main__.rroGroupIndex.remove(groupIndex)
		if body in __main__.rroBody:
			__main__.rroBody.remove(body)
		if itemIndex in __main__.rroItemIndex:
			__main__.rroItemIndex.remove(itemIndex)
		if suffix in __main__.rroSuffix:
			__main__.rroSuffix.remove(suffix)

		__main__.rroPrefix.append(prefix)
		__main__.rroGroupIndex.append(groupIndex)
		__main__.rroBody.append(body)
		__main__.rroItemIndex.append(itemIndex)
		__main__.rroSuffix.append(suffix)

		self.setupPopupMenus()

	def clearHistory(self,*arge):
		__main__.rroPrefix = []
		__main__.rroGroupIndex = []
		__main__.rroBody = []
		__main__.rroItemIndex = []
		__main__.rroSuffix = []
		__main__.rroSearch = []
		__main__.rroReplace = []

		cmds.popupMenu('prefixTextPopupMenu', edit=True, dai=True)
		cmds.popupMenu('groupIndexTextPopupMenu', edit=True, dai=True)
		cmds.popupMenu('bodyTextPopupMenu', edit=True, dai=True)
		cmds.popupMenu('itemIndexTextPopupMenu', edit=True, dai=True)
		cmds.popupMenu('suffixTextPopupMenu', edit=True, dai=True)
		cmds.popupMenu('searchTextPopupMenu', edit=True, dai=True)
		cmds.popupMenu('replaceTextPopupMenu', edit=True, dai=True)

		cmds.textField( 'prefixTextField', edit=True, text='' )
		cmds.textField( 'groupIndexTextField', edit=True, text='0' )
		cmds.textField( 'bodyTextField', edit=True, text='' )
		cmds.textField( 'itemIndexTextField', edit=True, text='0' )
		cmds.textField( 'suffixTextField', edit=True, text='' )
		cmds.textField( 'searchTextField', edit=True, text='' )
		cmds.textField( 'replaceTextField', edit=True, text='' )

	def setupPopupMenus(self):
		cmds.popupMenu('prefixTextPopupMenu', edit=True, dai=True)
		cmds.popupMenu('groupIndexTextPopupMenu', edit=True, dai=True)
		cmds.popupMenu('bodyTextPopupMenu', edit=True, dai=True)
		cmds.popupMenu('itemIndexTextPopupMenu', edit=True, dai=True)
		cmds.popupMenu('suffixTextPopupMenu', edit=True, dai=True)
		cmds.popupMenu('searchTextPopupMenu', edit=True, dai=True)
		cmds.popupMenu('replaceTextPopupMenu', edit=True, dai=True)

		for x,item in enumerate(reversed(__main__.rroPrefix)):
			cmds.menuItem( label=item, parent='prefixTextPopupMenu', command=eval('lambda x: ui.setTextFieldText("'+item+'","prefixTextField")') )

		for x,item in enumerate(reversed(__main__.rroGroupIndex)):
			cmds.menuItem( label=item, parent='groupIndexTextPopupMenu', command=eval('lambda x: ui.setTextFieldText("'+item+'","groupIndexTextField")') )

		for x,item in enumerate(reversed(__main__.rroBody)):
			cmds.menuItem( label=item, parent='bodyTextPopupMenu', command=eval('lambda x: ui.setTextFieldText("'+item+'","bodyTextField")') )

		for x,item in enumerate(reversed(__main__.rroItemIndex)):
			cmds.menuItem( label=item, parent='itemIndexTextPopupMenu', command=eval('lambda x: ui.setTextFieldText("'+item+'","itemIndexTextField")') )

		for x,item in enumerate(reversed(__main__.rroSuffix)):
			cmds.menuItem( label=item, parent='suffixTextPopupMenu', command=eval('lambda x: ui.setTextFieldText("'+item+'","suffixTextField")') )

		for x,item in enumerate(reversed(__main__.rroSearch)):
			cmds.menuItem( label=item, parent='searchTextPopupMenu', command=eval('lambda x: ui.setTextFieldText("'+item+'","searchTextField")') )

		for x,item in enumerate(reversed(__main__.rroReplace)):
			cmds.menuItem( label=item, parent='replaceTextPopupMenu', command=eval('lambda x: ui.setTextFieldText("'+item+'","replaceTextField")') )

	def setTextFieldText(self,text,textField):
		print('text = '+text)
		print('textField = '+textField)
		cmds.textField( textField, edit=True, text=text )

	def switchIndexes(self,*args):
		value = cmds.checkBox( 'switchIndexesCheckBox', query=True, v=True )

		layout = 'renameFormLayout'

		prefixTextTitle = 'prefixText'
		prefixTextField = 'prefixTextField'

		groupIndexTitle = 'groupIndexText'
		groupIndexField = 'groupIndexTextField'

		bodyTitle = 'bodyText'
		bodyField = 'bodyTextField'

		itemIndexTitle = 'itemIndexText'
		itemIndexField = 'itemIndexTextField'

		suffixTextTitle = 'suffixText'
		suffixTextField = 'suffixTextField'

		if value is False:
			attachControlData = [
				[groupIndexTitle,'top',5,prefixTextTitle],
				[bodyTitle,'top',5,groupIndexTitle],
				[itemIndexTitle,'top',5,bodyTitle],
				[suffixTextTitle,'top',5,itemIndexTitle]
			]

			cmds.formLayout( layout, edit=True, ac=attachControlData )

			attachControlData = [
				[groupIndexField,'top',5,prefixTextField],
				[bodyField,'top',5,groupIndexField],
				[itemIndexField,'top',5,bodyField],
				[suffixTextField,'top',5,itemIndexField]
			]

			cmds.formLayout( layout, edit=True, ac=attachControlData )

		else:
			attachControlData = [
				[itemIndexTitle,'top',5,prefixTextTitle],
				[bodyTitle,'top',5,itemIndexTitle],
				[groupIndexTitle,'top',5,bodyTitle],
				[suffixTextTitle,'top',5,groupIndexTitle]
			]

			cmds.formLayout( layout, edit=True, ac=attachControlData )

			attachControlData = [
				[itemIndexField,'top',5,prefixTextField],
				[bodyField,'top',5,itemIndexField],
				[groupIndexField,'top',5,bodyField],
				[suffixTextField,'top',5,groupIndexField]
			]

			cmds.formLayout( layout, edit=True, ac=attachControlData )


rename = Rename()
reorder = Reorder()
#group = Group()
ui = UI()

def startUI():
	ui.create()

