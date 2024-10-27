from PyQt5.QtWidgets import QComboBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont
from PyQt5.QtCore import Qt


class GroupedComboBox(QComboBox):
    def __init__(self, parent=None):
        super(GroupedComboBox, self).__init__(parent)
        self.setModel(QStandardItemModel(self))

    def addGroup(self, groupName, items):
        # Add the group name as a non-selectable item
        groupItem = QStandardItem('---' + groupName + '---')
        groupItem.setFlags(Qt.NoItemFlags)  # Make it non-selectable
        font = QFont()
        font.setBold(True)
        groupItem.setFont(font)
        self.model().appendRow(groupItem)

        # Add the items under the group
        for item in items:
            childItem = QStandardItem(item)
            self.model().appendRow(childItem)
