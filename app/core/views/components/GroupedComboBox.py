from PySide6.QtWidgets import QComboBox
from PySide6.QtGui import QStandardItemModel, QStandardItem, QFont
from PySide6.QtCore import Qt


class GroupedComboBox(QComboBox):
    """A custom QComboBox with grouped items, where each group has a non-selectable header.

    Extends QComboBox to support grouping items under non-selectable header items.
    Useful for organizing related options in a dropdown menu.
    """

    def __init__(self, parent=None):
        """Initialize the GroupedComboBox.

        Args:
            parent: Parent widget for the combo box. Defaults to None.
        """
        super(GroupedComboBox, self).__init__(parent)
        self.setModel(QStandardItemModel(self))

    def add_group(self, groupName, items):
        """Add a group of items under a non-selectable group header.

        Args:
            groupName: The name of the group (displayed as header).
            items: The items to add under the header. Each may be a plain
                string, or a ``(label, data)`` pair - the label is what the
                operator reads and the data is the caller's stable
                identifier, retrievable through the ordinary
                ``itemData`` / ``currentData`` / ``findData`` API.

                The pair form exists so a caller never has to read an
                identity back out of display text. Without it this widget
                offered no data role at all, which is why the algorithm
                combo routed on ``currentText()`` - and a translated label
                would then have matched nothing.
        """
        # Add the group name as a non-selectable item
        groupItem = QStandardItem('---' + groupName + '---')
        groupItem.setFlags(Qt.NoItemFlags)  # Make it non-selectable
        font = QFont()
        font.setBold(True)
        groupItem.setFont(font)
        self.model().appendRow(groupItem)

        # Add the items under the group
        for item in items:
            if isinstance(item, (tuple, list)):
                label, data = item
            else:
                label, data = item, None
            childItem = QStandardItem(label)
            if data is not None:
                # Qt.UserRole specifically: itemData/currentData/findData
                # all default to it, and QStandardItem.setData without a
                # role writes EditRole instead, which those readers do not
                # see.
                childItem.setData(data, Qt.UserRole)
            self.model().appendRow(childItem)
