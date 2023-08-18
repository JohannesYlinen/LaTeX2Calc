import sys
import os
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap, QIcon, QFont, QKeySequence, QPalette, QColor, QPainter, QBrush, QTransform
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QTextEdit, QApplication, QLabel, QShortcut, QFrame, QSizePolicy, QCheckBox, QSlider
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QScrollArea, QColorDialog, QDesktopWidget
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, QPoint, QSettings
from LaTeX2CalcAssets import translate
from LaTeX2CalcAssets import LaTeX2CalcEngine
engine = LaTeX2CalcEngine()

# ⚠️ WARNING: ENTERING HORRIBLY WRITTEN CODE ZONE ⚠️
# Abandon all hope, those who enter here.
# This code might make you question your life choices.

# DISCLAIMER: The author accepts no responsibility for
# any brain cells lost from attempting to comprehend this code.

# A word of advice: if you value your sanity, turn back now.
# If you choose to brave this madness, may the odds be ever in your favor.

# Proceed at your own risk! You've been warned.

class SettingsManager(QSettings):
    def __init__(self):
        super().__init__("Johannes Ylinen", "LaTeX2Calc")

    def save_variable(self, variable_name, variable_value):
        # Save the variable state and its data type
        self.setValue(variable_name, variable_value)

    def load_variable(self, variable_name, default_value, data_type):
        # Load the variable state and handle its data type
        try:
            return self.value(variable_name, default_value, type=data_type)
        except TypeError as e:
            return {}

theme_on = False
history_list_on = False
info_on = False

settings_manager = SettingsManager()

# settings
SC_on = settings_manager.load_variable("SC_on", False, bool)
TI_on = settings_manager.load_variable("TI_on", True, bool)
e_on = settings_manager.load_variable("e_on", False, bool)
i_on = settings_manager.load_variable("i_on", False, bool)
g_on = settings_manager.load_variable("g_on", False, bool)
stay_on_top_on = settings_manager.load_variable("stay_on_top_on", False, bool)
solve_button_on = settings_manager.load_variable("solve_button_on", False, bool)
ddx_on = settings_manager.load_variable("ddx_on", False, bool)
constants_on = settings_manager.load_variable("constants_on", False, bool)
coulomb_on = settings_manager.load_variable("coulomb_on", False, bool)

# theme
sliderStartValue = settings_manager.load_variable("sliderStartValue", 128, int)
userInputColor = settings_manager.load_variable("userInputColor", "", str)
inverse_theme = settings_manager.load_variable("inverse_theme", False, bool)
transparentWindowState = settings_manager.load_variable("transparentWindowState", False, bool)

# history
history = settings_manager.load_variable("history", {}, dict)
historyLen = settings_manager.load_variable("historyLen", 0, int)
# window pos
windowPos = settings_manager.load_variable("windowPos", None, QPoint)
windowDimensions = settings_manager.load_variable("windowDimensions", (650, 450), tuple)
if isinstance(windowDimensions, dict):
    windowDimensions = (650, 450)

# paste text
def paste_clipboard_text():
    clipboard = QApplication.clipboard()
    inputEdit.setPlainText(clipboard.text())

def translate_input():
    if not "ddx" in globals():
        return
    input_value = inputEdit.toPlainText()
    expression = input_value
    output_value = translate(expression, TI_on, SC_on, constants_on, coulomb_on, e_on, i_on, g_on)
    if ddx_on:
        ddx.setStyleSheet(toggle_button_on_style)
        if not solve_button_on:
            variable_line.hide()
        ddx_line.show()
        ddx_nth.show()
        variable = ddx_line.text()
        nth = ddx_nth.text()
        if not variable:
            variable = 'x'
        else:
            variable = engine.translateGreekLetters(variable)
            variable = engine.translateLowerIndex(variable)
            variable = engine.translateLowerIndexazAZ(variable)
        if not nth:
            output_value = f'({output_value},{variable})'
        else:    
            nth = engine.translateGreekLetters(nth)
            nth = engine.translateLowerIndex(nth)
            nth = engine.translateLowerIndexazAZ(nth)
            output_value = f'({output_value},{variable},{nth})'
    else:
        ddx.setStyleSheet(toggle_button_off_style)
        ddx_line.hide()
        ddx_nth.hide()

    if solve_button_on: 
        solve_button.setStyleSheet(toggle_button_on_style)
        variable_line.show()
        variable = variable_line.text()
        if not variable:
            variable = 'x'
        else:
            variable = engine.translateGreekLetters(variable)
            variable = engine.translateLowerIndex(variable)
            variable = engine.translateLowerIndexazAZ(variable)
        output_value = f"solve({output_value},{variable})"
    else:
        solve_button.setStyleSheet(toggle_button_off_style)
        variable_line.hide()
    
    outputEdit.setText(output_value)

def copy_to_clipboard():
    global history, historyLen
    translation = outputEdit.toPlainText()
    if translation:
        latex = inputEdit.toPlainText()
        clipboard = QApplication.clipboard()
        
        # check for duplicate translations OK
        if translation in history:
            try:
                del history[latex]
                historyLen -= 1
            except KeyError as e:
                pass

        # copy and add translation to history
        clipboard.setText(translation)
        history[latex] = translation
        historyLen += 1

        # delete oldest copy if history lenght exceeds 100
        if historyLen > 100:
            del history[next(iter(history))]
            historyLen -= 1

    # reset history
    if history_list_on:
        history_list_clicked()
        history_list_clicked()
    
def hide_history():
    history_button.setStyleSheet(selection_off_style)
    history_border.hide()
    history_selection.hide()
    history_text.hide()
    clear_history_button.hide()
    if historyLen > 0:
        scroll.setParent(None)

def hide_info():
    info_page.hide()
    info_border.hide()
    header_text.hide()
    info_text.hide()
    action_text.hide()
    info_button.setStyleSheet(selection_off_style + "QPushButton {font-size: 30px; }")

def show_info():
    info_page.show()
    info_border.show()
    header_text.show()
    info_text.show()
    action_text.show()
    info_button.setStyleSheet(selection_on_style + "QPushButton {font-size: 30px; }")

def hide_theme():
    theme_button.setStyleSheet(selection_off_style)
    theme_selection_border.hide()
    theme_selection.hide()
    themeLine.hide()
    colorButton.hide()
    alphaSlider.hide()
    alphaSlider.label.hide()
    light_mode.hide()
    transparent_window.hide()

def show_theme():
    theme_button.setStyleSheet(selection_on_style)
    theme_selection_border.show()
    theme_selection.show()
    themeLine.show()
    colorButton.show()
    alphaSlider.show()
    alphaSlider.label.show()
    light_mode.show()
    transparent_window.show()

def theme_selection_clicked():
    global theme_on, history_list_on, info_on
    theme_on = not theme_on

    if info_on:
        info_on = False
        hide_info()

    if history_list_on:
        history_list_on = False
        hide_history()

    if theme_on:
        show_theme()
    else:
        hide_theme()

def applyDefaultTheme():
    if hasattr(window, "background"):
        window.createBackground(1)
    else:
        window.createBackground(1)

    if transparentWindowState:
        window.setNewColor("transparent")
    elif inverse_theme:
        window.setNewColor("white")
    else:
        window.setNewColor("black")
    clear_history_button.addStyle(selection_off_style + "QPushButton {color: rgba(255,255,255,200); background-color: rgba(0, 0, 0, 200)}")

    backScreen.setNewColor("black")
    backScreenSmall.setNewColor("black")

    history_selection.setNewColor("#0b0f13")
    theme_selection.setNewColor("#0b0f13")
    info_page.setNewColor("#0b0f13")
    color = "white" if inverse_theme else "#192328"
    history_border.setNewColor(color)
    theme_selection_border.setNewColor(color)
    info_border.setNewColor(color)

def getCustomColor(presetColor=False):
    if presetColor:
        if hasattr(window, "background"):
           window.background.hide()

        color = f'rgb({presetColor.red()},{presetColor.green()},{presetColor.blue()})'
        backScreen.setNewColor(color)
        backScreenSmall.setNewColor(color)
        locCol = "rgba(0,0,0,200)" if not inverse_theme else "rgba(255,255,255,200)"
        colCheck = color if inverse_theme else "white"
        clear_history_button.addStyle(selection_off_style + str("QPushButton {background-color: " + locCol + ";}" "QPushButton:hover {color: " + colCheck + "; background-color: " + locCol + ";}")) 
        history_selection.setNewColor(color)
        theme_selection.setNewColor(color)
        info_page.setNewColor(color)
        return color
    else:
        color = themeLine.text().replace(' ', '')
        if color:
            if hasattr(window, "background"):
                window.background.hide()
            backScreen.setNewColor(color)
            backScreenSmall.setNewColor(color)
            locCol = "rgba(0,0,0,200)" if not inverse_theme else "rgba(255,255,255,200)"
            colCheck = color if inverse_theme else "white"
            clear_history_button.addStyle(selection_off_style + str("QPushButton {background-color: " + locCol + ";}" "QPushButton:hover {color: " + colCheck + "; background-color: " + locCol + ";}")) 

            if 'rgb' in color or '#' in color:
                backScreen.setNewColor(color)
                backScreenSmall.setNewColor(color)
                history_selection.setNewColor(color)
                theme_selection.setNewColor(color)
                info_page.setNewColor(color)
                updateInverse()

            elif QColor.isValidColor(color): 
                colorSource = QColor(color)
                rawColors = colorSource.getRgb()
                rgba = f'rgba{rawColors}'.replace(' ', '')
                history_selection.setNewColor(rgba)
                theme_selection.setNewColor(rgba)
                info_page.setNewColor(rgba)
                updateInverse()

            else:
                applyDefaultTheme()
        else:
            applyDefaultTheme()

        return color

def clear_history():
    history_list_clicked(True)
    history_list_clicked()

def update_history():
    global scroll
    scroll = ScrollClass()
    scroll.setStyleSheet(history_button_style) 
    scroll.setParent(window)
    scroll.show()

def history_list_clicked(reset=False):
    global history_list_on, theme_on, history, scroll, info_on, historyLen
    if reset:
        history = {}
        historyLen = 0
        if "scroll" in globals():
            scroll.setParent(None)
        
    history_list_on = not history_list_on
    if info_on:
        info_on = False
        hide_info()

    if theme_on:
        theme_on = False
        hide_theme()

    if history_list_on:
        if historyLen == 0:
            history_selection.setGeometry(224+move, 50, 225, 50)
            history_border.setGeometry(224+move-border_width, 50-border_width, 225+border_width*2, 50+border_width*2)

            history_text.show()
        else:
            history_text.hide()
            update_history()
            
            scroll.updateScrollClass()
            window.resizeEvent(event=None, backGround=False)
            
        history_button.setStyleSheet(selection_on_style)
        history_border.show()
        history_selection.show()    
        clear_history_button.show()
        clear_history_button.raise_()
    else:
        clear_history_button.hide()
        history_button.setStyleSheet(selection_off_style)
        history_border.hide()
        history_selection.hide()
        history_text.hide()
        if historyLen > 0 and "scroll" in globals():
            scroll.setParent(None)

def info_button_clicked():
    global info_on, history_list_on, theme_on
    info_on = not info_on
    
    if history_list_on:
        history_list_on = False
        hide_history()

    if theme_on:
        theme_on = False
        hide_theme()

    if info_on:
        show_info()
    else:
        hide_info()

def about_button_clicked():
    window.open_info_window()

def SC_button_clicked():
    global SC_on, TI_on, e_on
    if e_on:
        e_button_clicked()
    if i_on:
        i_button_clicked()
    if g_on:
        g_button_clicked()
    if TI_on:
        TI_button_clicked()
    SC_on = not SC_on
    if not SC_on:
        translate_input()
        SC_button.setStyleSheet(toggle_button_off_style)
    else:
        SC_button.setStyleSheet(toggle_button_on_style)
        translate_input()

def TI_button_clicked():
    global TI_on, solve_button_on, ddx_on
    if SC_on:
        SC_button_clicked()
    if e_on:
        e_button_clicked()
    if i_on:
        i_button_clicked()
    if g_on:
        g_button_clicked()
    if constants_on:
        constants_button_clicked()
    if coulomb_on:
        coulomb_button_clicked()
    TI_on = not TI_on

    if not TI_on:
        translate_input()
        TI_button.setStyleSheet(toggle_button_off_style)
        if ddx_on:
            ddx_on = not ddx_on 
            ddx.setStyleSheet(toggle_button_off_style)
            translate_input()

        if solve_button_on:
            solve_button_on = not solve_button_on
            solve_button.setStyleSheet(toggle_button_off_style)
            variable_line.hide()
            translate_input()
    else:
        TI_button.setStyleSheet(toggle_button_on_style)
        translate_input()

def constants_button_clicked():
    global constants_on
    if not SC_on:
        constants_on = not constants_on
        translate_input()
        if constants_on:
            constants_button.setStyleSheet(toggle_button_on_style)
        else:
            constants_button.setStyleSheet(toggle_button_off_style)

def coulomb_button_clicked():
    global coulomb_on
    if not SC_on:
        coulomb_on = not coulomb_on
        translate_input()
        if coulomb_on:
            coulomb_button.setStyleSheet(toggle_button_on_style)
        else:
            coulomb_button.setStyleSheet(toggle_button_off_style)
def e_button_clicked():
    global e_on
    if TI_on:
        e_on = not e_on
        if not e_on:
            translate_input()
            e_button.setStyleSheet(toggle_button_off_style)
        else:
            e_button.setStyleSheet(toggle_button_on_style)
            translate_input()
def i_button_clicked():
    global i_on
    if TI_on:
        i_on = not i_on
        if not i_on:
            translate_input()
            i_button.setStyleSheet(toggle_button_off_style)
        else:
            i_button.setStyleSheet(toggle_button_on_style)
            translate_input()
def g_button_clicked():
    global g_on
    if TI_on:
        g_on = not g_on
        if not g_on:
            translate_input()
            g_button.setStyleSheet(toggle_button_off_style)
        else:
            g_button.setStyleSheet(toggle_button_on_style)
            translate_input()

def toggle_stay_on_top():
    global stay_on_top_on
    stay_on_top_on = not stay_on_top_on
    if stay_on_top_on:
        window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)
        stay_on_top_button.setStyleSheet(toggle_button_on_style)
        if hasattr(window, "background"):
            window.background.setParent(None)
            window.background.deleteLater()
            window.resizeEvent(None)
    else:
        window.setWindowFlags(window.windowFlags() & ~Qt.WindowStaysOnTopHint)
        stay_on_top_button.setStyleSheet(toggle_button_off_style)
    window.show()

def reset_settings():
    settings_manager.clear()

def solve_button_clicked():
    global solve_button_on
    if TI_on:
        solve_button_on = not solve_button_on
        if not solve_button_on:
            solve_button.setStyleSheet(toggle_button_off_style)
            variable_line.hide()
            translate_input()
            window.resizeEvent(event=None, backGround=False)
        else:
            solve_button.setStyleSheet(toggle_button_on_style)
            variable_line.show()
            translate_input()
            window.resizeEvent(event=None, backGround=False)
def ddx_clicked():
    global ddx_on
    window.resizeEvent(event=None, backGround=False)
    if TI_on:
        ddx_on = not ddx_on
        if not ddx_on:
            ddx.setStyleSheet(toggle_button_off_style)
            translate_input()
            window.resizeEvent(event=None, backGround=False)
        else:
            ddx.setStyleSheet(toggle_button_on_style)
            translate_input()
            window.resizeEvent(event=None, backGround=False)

def on_quick_button_clicked():
    paste_clipboard_text()
    translate_input()
    copy_to_clipboard() 

def close_selection():
    if theme_on:
        theme_selection_clicked()
    if history_list_on:
        history_list_clicked()
    if info_on:
        info_button_clicked()

def clearTextFocus():
    inputEdit.clearFocus()
    outputEdit.clearFocus()
    variable_line.clearFocus()
    ddx_line.clearFocus()
    ddx_nth.clearFocus()
    close_selection()

def chooseColors(inverse_theme):
    global alphaWhite, text, BLACK, WHITE, button_alpha, selection_style, tool_bar_style, buttonStyle, toggle_button_off_style, toggle_button_on_style, text_edit_style, close_buttonStyle, selection_off_style, selection_on_style, history_button_style, checkbox_style
    
    colorComponents = None
    rgba = None
    if 'themeLine' in globals():
        color = themeLine.text().replace(' ', '')
        colorComponents = getColorComponents(color)
            
        if QColor.isValidColor(color): 
            colorSource = QColor(color)
            rgba = colorSource.getRgb()

    if inverse_theme:        
        if colorComponents or rgba:
            if colorComponents:
                red, green, blue, alpha = colorComponents
            else:
                red, green, blue, alpha = rgba
            color = themeLine.text().replace(' ', '')
            text = f'rgba{red, green, blue, 255}'
            history_text_style = text
            alphaWhite = "rgba(255, 255, 255, 160)"
            selection_style = f"rgba{red, green, blue, 30}"
            lightToggleOffHover = f"rgba{red, green, blue, 120}"
        else:
            text = "rgba(0, 0, 0, 180)"
            history_text_style = "black"
            alphaWhite = "rgba(255, 255, 255, 190)"
            selection_style = "rgba(230, 220, 215, 125)"
            lightToggleOffHover = selection_style

        BLACK = "white"
        WHITE = "black"
        button_alpha = "rgba(0, 0, 0, 100)"

        tool_bar_style = "QFrame { background-color: rgba(255, 255, 255, 155); border-radius: 10px;}"
        buttonStyle = ("QPushButton {background-color: " + alphaWhite + "; color: " + text + "; font-size: 20px; border-radius: 10px;}" "QPushButton:hover {background-color: " + alphaWhite + "; color: white;}")
        toggle_button_off_style = ("QPushButton {background-color: " + alphaWhite + "; color: " + text + "; font-size: 20px; border-radius: 10px;}" "QPushButton:hover {background-color: " + lightToggleOffHover + "; color:" + BLACK + " ;}")
        close_buttonStyle = ("QPushButton {background-color: transparent; color: " + text + "; font-size: 50px; border-radius: 10px;}" "QPushButton:hover {background-color: transparent; color: white;}")
        selection_off_style = ("QPushButton {background-color: transparent; color: " + text + "; font-size: 20px; border-radius: 10px;}" "QPushButton:hover {background-color: " + selection_style + "; color: " + "white" + ";}")
        selection_on_style = ("QPushButton {background-color: " + selection_style + "; color: " + text + "; font-size: 20px; border-radius: 10px;}" "QPushButton:hover {background-color: " + selection_style + "; color: " + "white" + ";}")
        history_button_style = ("QPushButton {color: " + alphaWhite + "; font-size: 20px; border-radius: 10px;}" "QPushButton:hover {color: white;}")
        
    else:
        if colorComponents or rgba:
            if colorComponents:
                red, green, blue, alpha = colorComponents
            else:
                red, green, blue, alpha = rgba

            history_text_style = f'rgba{red, green, blue, 255}'
            selection_style = f"rgba{red, green, blue, 50}"
        else:
            history_text_style = "white"
            selection_style = "rgba(25, 35, 40, 130)"

        alphaWhite = "rgba(0, 0, 0, 60)"
        text = "rgba(255, 255, 255, 190)"
        BLACK = "black"
        WHITE = "white"
        button_alpha = "rgba(255, 255, 255, 150)"

        tool_bar_style = "QFrame { background-color: rgba(0, 0, 0, 100); border-radius: 10px;}"
        buttonStyle = ("QPushButton {background-color: " + alphaWhite + "; color: " + button_alpha + "; font-size: 20px; border-radius: 10px;}" "QPushButton:hover {background-color: " + alphaWhite + "; color: white;}")
        toggle_button_off_style = ("QPushButton {background-color: " + alphaWhite + "; color: " + text + "; font-size: 20px; border-radius: 10px;}" "QPushButton:hover {background-color: " + button_alpha + "; color:" + BLACK + " ;}")
        close_buttonStyle = ("QPushButton {background-color: transparent; color: " + button_alpha + "; font-size: 50px; border-radius: 10px;}" "QPushButton:hover {background-color: transparent; color: white;}")
        selection_off_style = ("QPushButton {background-color: transparent; color: " + text + "; font-size: 20px; border-radius: 10px;}" "QPushButton:hover {background-color: " + selection_style + "; color: white;}")
        selection_on_style = ("QPushButton {background-color: " + selection_style + "; color: white; font-size: 20px; border-radius: 10px;}" "QPushButton:hover {background-color: " + selection_style + "; color: white;}")
        history_button_style = ("QPushButton {color: " + text + "; font-size: 20px; border-radius: 10px;}" "QPushButton:hover {color: white;}")

    toggle_button_on_style = ("QPushButton {background-color: " + text + "; color: " + BLACK + "; font-size: 20px; border-radius: 10px;}" "QPushButton:hover {background-color: " + text +  "; color:" + BLACK + " ;}")
    text_edit_style = "background-color: " + alphaWhite + "; color:" + text + "; font-size: 16px; border-radius: 10px;"


    alphaWhite = "rgba(0, 0, 0, 60)"
    text = "rgba(255, 255, 255, 190)"
    WHITE = "white"
    checkbox_style = (""" 
        QCheckBox {
            color: """ + text + """;
        }
                        
        QCheckBox::indicator {
            width: 20px;
            height: 20px;
        }

        QCheckBox::indicator:unchecked {
            border: 2px solid """ + WHITE + """;
            background-color: """ + alphaWhite + """;
        }

        QCheckBox::indicator:checked {
            border: 2px solid """ + WHITE + """;
            background-color: """ + text + """;
        }
        """)
    
    return history_text_style

def inverseColors(inverse_theme):
    temp_history_text_color = chooseColors(inverse_theme)
    alphaSlider.addStyle("white", alphaWhite)

    if transparentWindowState:
        window.setNewColor("transparent")
    else:
        window.setNewColor(BLACK)

    if themeLine.text() == '' and not inverse_theme:
        color = "#192328"
    else:
        color = BLACK

    info_border.setNewColor(color)
    theme_selection_border.setNewColor(color)
    light_mode.setStyleSheet(checkbox_style)
    transparent_window.setStyleSheet(checkbox_style)
    history_border.setNewColor(color)

    locCol = temp_history_text_color if inverse_theme else "white"
    bgCol = "rgba(0,0,0,150)" if not inverse_theme else "rgba(255,255,255,200)"
    clear_history_button.addStyle(selection_off_style + str("QPushButton {background-color: " + bgCol + ";}" "QPushButton:hover {color: " + locCol + "; background-color: " + BLACK + ";}")) 

    inputEdit.setStyleSheet(text_edit_style)
    outputEdit.setStyleSheet(text_edit_style)
    variable_line.setStyleSheet(text_edit_style)
    ddx_line.setStyleSheet(text_edit_style)
    ddx_nth.setStyleSheet(text_edit_style)
    pasteButton.setStyleSheet(buttonStyle)
    quickButton.setStyleSheet(buttonStyle)
    copyButton.setStyleSheet(buttonStyle)
    about_button.setStyleSheet(selection_off_style)
    ToolBar.setStyleSheet(tool_bar_style)
    minimize_button.setStyleSheet(close_buttonStyle)
    close_button.setStyleSheet(close_buttonStyle)

    # main buttons
    def set_toggle_button_style(widget, on):
        state = "on" if on else "off"
        widget.setStyleSheet(globals().get(f"toggle_button_{state}_style"))

    def set_selection_style(widget, on, additionalStyle=None):
        state = "on" if on else "off"
        if additionalStyle: 
            widget.setStyleSheet(globals().get(f"selection_{state}_style") + additionalStyle)
        else:
            widget.setStyleSheet(globals().get(f"selection_{state}_style"))

    set_toggle_button_style(stay_on_top_button, stay_on_top_on)
    set_toggle_button_style(SC_button, SC_on)
    set_toggle_button_style(TI_button, TI_on)
    set_toggle_button_style(constants_button, constants_on)
    set_toggle_button_style(coulomb_button, coulomb_on)
    set_toggle_button_style(e_button, e_on)
    set_toggle_button_style(i_button, i_on)
    set_toggle_button_style(g_button, g_on)
    set_toggle_button_style(solve_button, solve_button_on)
    set_toggle_button_style(ddx, ddx_on)

    set_selection_style(theme_button, theme_on)
    set_selection_style(history_button, history_list_on)
    set_selection_style(info_button, info_on, "QPushButton {font-size: 30px;}")

def updateInverse():
    inverseColors(inverse_theme)
    inverseColors(inverse_theme)    

def updateBackScreen():
    backScreen.setNewColor(backScreen.color)
    backScreenSmall.setNewColor(backScreenSmall.color)

# get colors for theme
chooseColors(inverse_theme)

def inverseTheme():
    saveSettings()
    global inverse_theme
    inverse_theme = not inverse_theme
    inverseColors(inverse_theme)

def changeWindowState():
    saveSettings()
    global transparentWindowState
    transparentWindowState = not transparentWindowState
    inverseColors(inverse_theme)

def getColorValues(color):
    colorValues = color.split('(', 1)[-1].split(')', 1)[0].split(",")
    for i in range(len(colorValues)):
        if colorValues[i] == '':
            colorValues[i] = '0'
        if not colorValues[i].isdigit():
            return
        elif int(colorValues[i]) > 255:
            colorValues[i] = 255
    return colorValues

def getColorComponents(color):
    if isinstance(color, QColor):
        colorValues = (color.red(), color.green(), color.blue(), color.alpha())
        red, green, blue, alpha = map(int, colorValues)
    
    elif 'rgba(' in color and color.count(',') == 3:
        colorValues = getColorValues(color)
        if not colorValues or len(colorValues) != 4:
            return
        red, green, blue, alpha = map(int, colorValues)

    elif 'rgb(' in color and color.count(',') == 2 and not 'rgba' in color:
        alpha = 255
        colorValues = getColorValues(color)
        if not colorValues or len(colorValues) != 3:
            return
        red, green, blue = map(int, colorValues)

    elif QColor.isValidColor(color):
        alpha = 255
        colorValues = getColorValues(color)
        if not colorValues:
            return
        red, green, blue = map(int, colorValues)
    else:
        return None
    
    return red, green, blue, alpha

def positionWindow(window):
    qr = window.frameGeometry()
    cp = QDesktopWidget().availableGeometry().center()
    qr.moveCenter(cp)
    window.move(qr.topLeft())   

def getScreenRes():
    desktop = QApplication.desktop()
    screen_resolution = (desktop.width(), desktop.height())
    return screen_resolution

# CLASSES
class MainWindow(QWidget):
    def __init__(self, color, resizeBorderWidth):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.color = color

        self.resizeBorderWidth = resizeBorderWidth
        self.setMinimumSize(200, 150)

        self.is_resizing_top = False
        self.is_resizing_bottom = False
        self.is_resizing_left = False
        self.is_resizing_right = False
        self.is_resizing_top_left = False
        self.is_resizing_top_right = False
        self.is_resizing_bottom_left = False
        self.is_resizing_bottom_right = False
        self.setup_resize_handles()

        if stay_on_top_on:    
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
    
    def open_info_window(self):
        self.info_window = InfoWindow()
        self.info_window.show()
        
    def closeEvent(self, event):
        saveSettings(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(self.color))) # valikkojen default color "#0b0f13", ikkunan "black"
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10,10)

    def setNewColor(self, color):
        colorComponents = getColorComponents(color)
        if colorComponents:
            red, green, blue, alpha = colorComponents
            self.color = QColor(red, green, blue, alpha)
            self.update()

        else:
            self.color = QColor(color)
            self.update()

    def setup_resize_handles(self):
        resizeBorderWidth = self.resizeBorderWidth

        # Top resize handle
        self.top_resize_handle = QWidget(self)
        self.top_resize_handle.setGeometry(resizeBorderWidth, 0, self.width() - 2 * resizeBorderWidth, resizeBorderWidth)
        self.top_resize_handle.setStyleSheet("background-color: transparent;") #darkGray
        self.top_resize_handle.setCursor(Qt.SizeVerCursor)

        # Bottom resize handle
        self.bottom_resize_handle = QWidget(self)
        self.bottom_resize_handle.setGeometry(resizeBorderWidth, self.height() - resizeBorderWidth, self.width() - 2 * resizeBorderWidth, resizeBorderWidth)
        self.bottom_resize_handle.setStyleSheet("background-color: transparent;")
        self.bottom_resize_handle.setCursor(Qt.SizeVerCursor)

        # Left resize handle
        self.left_resize_handle = QWidget(self)
        self.left_resize_handle.setGeometry(0-10, resizeBorderWidth, resizeBorderWidth, self.height() - 2 * resizeBorderWidth)
        self.left_resize_handle.setStyleSheet("background-color: transparent;")
        self.left_resize_handle.setCursor(Qt.SizeHorCursor)

        # Right resize handle
        self.right_resize_handle = QWidget(self)
        self.right_resize_handle.setGeometry(self.width() - resizeBorderWidth, resizeBorderWidth, resizeBorderWidth, self.height() - 2 * resizeBorderWidth)
        self.right_resize_handle.setStyleSheet("background-color: transparent;")
        self.right_resize_handle.setCursor(Qt.SizeHorCursor)

        # Top-left resize handle
        self.top_left_resize_handle = QWidget(self)
        self.top_left_resize_handle.setGeometry(0, 0, resizeBorderWidth, resizeBorderWidth)
        self.top_left_resize_handle.setStyleSheet("background-color: transparent;")
        self.top_left_resize_handle.setCursor(Qt.SizeFDiagCursor)

        # Top-right resize handle
        self.top_right_resize_handle = QWidget(self)
        self.top_right_resize_handle.setGeometry(self.width() - resizeBorderWidth, 0, resizeBorderWidth, resizeBorderWidth)
        self.top_right_resize_handle.setStyleSheet("background-color: transparent;")
        self.top_right_resize_handle.setCursor(Qt.SizeBDiagCursor)

        # Bottom-left resize handle
        self.bottom_left_resize_handle = QWidget(self)
        self.bottom_left_resize_handle.setGeometry(0, self.height() - resizeBorderWidth, resizeBorderWidth, resizeBorderWidth)
        self.bottom_left_resize_handle.setStyleSheet("background-color: transparent;")
        self.bottom_left_resize_handle.setCursor(Qt.SizeBDiagCursor)

        # Bottom-right resize handle
        self.bottom_right_resize_handle = QWidget(self)
        self.bottom_right_resize_handle.setGeometry(self.width() - resizeBorderWidth, self.height() - resizeBorderWidth, resizeBorderWidth, resizeBorderWidth)
        self.bottom_right_resize_handle.setStyleSheet("background-color: transparent;")
        self.bottom_right_resize_handle.setCursor(Qt.SizeFDiagCursor)

    def mousePressEvent(self, event):
        if self.top_resize_handle.geometry().contains(event.pos()):
            self.is_resizing_top = True
            self.resize_origin = event.globalPos()
            self.original_geometry = self.geometry()

        elif self.bottom_resize_handle.geometry().contains(event.pos()):
            self.is_resizing_bottom = True
            self.resize_origin = event.globalPos()
            self.original_geometry = self.geometry()

        elif self.left_resize_handle.geometry().contains(event.pos()):
            self.is_resizing_left = True
            self.resize_origin = event.globalPos()
            self.original_geometry = self.geometry()

        elif self.right_resize_handle.geometry().contains(event.pos()):
            self.is_resizing_right = True
            self.resize_origin = event.globalPos()
            self.original_geometry = self.geometry()

        elif self.top_left_resize_handle.geometry().contains(event.pos()):
            self.is_resizing_top_left = True
            self.resize_origin = event.globalPos()
            self.original_geometry = self.geometry()

        elif self.top_right_resize_handle.geometry().contains(event.pos()):
            self.is_resizing_top_right = True
            self.resize_origin = event.globalPos()
            self.original_geometry = self.geometry()

        elif self.bottom_left_resize_handle.geometry().contains(event.pos()):
            self.is_resizing_bottom_left = True
            self.resize_origin = event.globalPos()
            self.original_geometry = self.geometry()

        elif self.bottom_right_resize_handle.geometry().contains(event.pos()):
            self.is_resizing_bottom_right = True
            self.resize_origin = event.globalPos()
            self.original_geometry = self.geometry()

        if not (
            self.is_resizing_top or
            self.is_resizing_top_left or
            self.is_resizing_top_right or
            self.is_resizing_bottom_left or
            self.is_resizing_bottom_right or
            self.is_resizing_bottom or
            self.is_resizing_left or
            self.is_resizing_right
                ):
            
            clearTextFocus()

    def mouseMoveEvent(self, event):
        if self.is_resizing_top:
            diff_y = event.globalPos().y() - self.resize_origin.y()
            new_height = self.original_geometry.height() - diff_y
            new_y = self.original_geometry.y() + diff_y
            self.setGeometry(self.x(), new_y, self.width(), new_height)

        elif self.is_resizing_bottom:
            diff_y = event.globalPos().y() - self.resize_origin.y()
            new_height = self.original_geometry.height() + diff_y
            self.setGeometry(self.x(), self.y(), self.width(), new_height)

        elif self.is_resizing_left:
            diff_x = event.globalPos().x() - self.resize_origin.x()
            new_width = self.original_geometry.width() - diff_x
            new_x = self.original_geometry.x() + diff_x
            self.setGeometry(new_x, self.y(), new_width, self.height())

        elif self.is_resizing_right:
            diff_x = event.globalPos().x() - self.resize_origin.x()
            new_width = self.original_geometry.width() + diff_x
            self.setGeometry(self.x(), self.y(), new_width, self.height())

        elif self.is_resizing_top_left:
            diff_x = event.globalPos().x() - self.resize_origin.x()
            diff_y = event.globalPos().y() - self.resize_origin.y()
            new_width = self.original_geometry.width() - diff_x
            new_height = self.original_geometry.height() - diff_y
            new_x = self.original_geometry.x() + diff_x
            new_y = self.original_geometry.y() + diff_y
            self.setGeometry(new_x, new_y, new_width, new_height)

        elif self.is_resizing_top_right:
            diff_x = event.globalPos().x() - self.resize_origin.x()
            diff_y = event.globalPos().y() - self.resize_origin.y()
            new_width = self.original_geometry.width() + diff_x
            new_height = self.original_geometry.height() - diff_y
            new_y = self.original_geometry.y() + diff_y
            self.setGeometry(self.x(), new_y, new_width, new_height)

        elif self.is_resizing_bottom_left:
            diff_x = event.globalPos().x() - self.resize_origin.x()
            diff_y = event.globalPos().y() - self.resize_origin.y()
            new_width = self.original_geometry.width() - diff_x
            new_height = self.original_geometry.height() + diff_y
            new_x = self.original_geometry.x() + diff_x
            self.setGeometry(new_x, self.y(), new_width, new_height)

        elif self.is_resizing_bottom_right:
            diff_x = event.globalPos().x() - self.resize_origin.x()
            diff_y = event.globalPos().y() - self.resize_origin.y()
            new_width = self.original_geometry.width() + diff_x
            new_height = self.original_geometry.height() + diff_y
            self.setGeometry(self.x(), self.y(), new_width, new_height)

    def mouseReleaseEvent(self, event):
        self.is_resizing_top = False
        self.is_resizing_bottom = False
        self.is_resizing_left = False
        self.is_resizing_right = False
        self.is_resizing_top_left = False
        self.is_resizing_top_right = False
        self.is_resizing_bottom_left = False
        self.is_resizing_bottom_right = False
        if "scroll" in globals():
            scroll.updateScrollClass()

    def createBackground(self, resizeBorderWidth):
        img = load_and_process_image(dir_path + "\\bar_dark_blur_crop2.png", self.width()-2*resizeBorderWidth, self.height()-2*resizeBorderWidth)
        rounded_img = create_rounded_pixmap(img, radius)
        new_background = create_and_configure_label(window, rounded_img, resizeBorderWidth, resizeBorderWidth, self.width()-2*resizeBorderWidth, self.height()-2*resizeBorderWidth)

        if hasattr(self, "background"):
            self.background.setParent(None)
            self.background.deleteLater()

        self.background = new_background
        self.background.show()
        self.background.stackUnder(inputEdit)

    def resizeEvent(self, event, backGround=True):
        super().resizeEvent(event)
        resizeBorderWidth = self.resizeBorderWidth

        self.top_resize_handle.setGeometry(resizeBorderWidth, 0, self.width() - 2 * resizeBorderWidth, resizeBorderWidth)
        self.bottom_resize_handle.setGeometry(resizeBorderWidth, self.height() - resizeBorderWidth, self.width() - 2 * resizeBorderWidth, resizeBorderWidth)
        self.left_resize_handle.setGeometry(0, resizeBorderWidth, resizeBorderWidth, self.height() - 2 * resizeBorderWidth)
        self.right_resize_handle.setGeometry(self.width() - resizeBorderWidth, resizeBorderWidth, resizeBorderWidth, self.height() - 2 * resizeBorderWidth)

        self.top_left_resize_handle.setGeometry(0, 0, resizeBorderWidth, resizeBorderWidth)
        self.top_right_resize_handle.setGeometry(self.width() - resizeBorderWidth, 0, resizeBorderWidth, resizeBorderWidth)
        self.bottom_left_resize_handle.setGeometry(0, self.height() - resizeBorderWidth, resizeBorderWidth, resizeBorderWidth)
        self.bottom_right_resize_handle.setGeometry(self.width() - resizeBorderWidth, self.height() - resizeBorderWidth, resizeBorderWidth, resizeBorderWidth)

        handles = [self.top_resize_handle, self.bottom_resize_handle, self.left_resize_handle, self.right_resize_handle,
                   self.top_left_resize_handle, self.top_right_resize_handle, self.bottom_left_resize_handle, self.bottom_right_resize_handle]

        for handle in handles:
            handle.raise_()

        resizeBorderWidth = 1


        if themeLine.text() == '' and backGround:
            self.createBackground(resizeBorderWidth)
            applyDefaultTheme()
            
        scale = min(int(self.width() / 850) * 0.07, 0.28)
        windowSplitFactor = 425/670 + scale
        backScreen.setGeometry(resizeBorderWidth, resizeBorderWidth, self.width()-2*resizeBorderWidth, self.height()-2*resizeBorderWidth)
        backScreenSmall.setGeometry(resizeBorderWidth, resizeBorderWidth, round(self.width()*windowSplitFactor), self.height()-2*resizeBorderWidth)

        draggableBar.setGeometry(resizeBorderWidth, resizeBorderWidth, window.width()-2*resizeBorderWidth, draggableBar.height())
        ToolBar.setGeometry(resizeBorderWidth, resizeBorderWidth, window.width()-2*resizeBorderWidth, 54)
        minimize_button.move(window.width()-resizeBorderWidth-minimize_button.width()-close_button.width(), 0)
        close_button.move(window.width()-resizeBorderWidth-close_button.width(), resizeBorderWidth)

        theme_button.move(theme_button.x(), 10+resizeBorderWidth)
        history_button.move(history_button.x(), 10+resizeBorderWidth)

        start_x = 430
        if self.width() > start_x:
            if historyLen > 0:
                if "scroll" in globals():
                    scroll.updateScrollClass()
                    history_selection.setGeometry(history_selection.x(), history_selection.y(), round(225 + windowSplitFactor * (self.width() - start_x)), scroll.height()+20)
                    history_border.setGeometry(history_border.x(), history_border.y(), round(225 + windowSplitFactor * (self.width() - start_x) + 2), scroll.height()+2+20)

                    
            else:
                history_border.setGeometry(224+move-border_width, 50-border_width, 225+border_width*2, 50+border_width*2)
                history_selection.setGeometry(224+move, 50, 225, 50)
        else:
            if historyLen > 0:
                if "scroll" in globals():
                    scroll.updateScrollClass()
                    scroll.setFixedWidth(255-40)
                    scroll.scrollArea.setFixedWidth(255-40)
                    history_selection.setGeometry(history_selection.x(), history_selection.y(), 225, scroll.height()+20)
                    history_border.setGeometry(history_border.x(), history_border.y(), 225 + 2, scroll.height()+20+2)

                    for button in scroll.buttons:
                        button.setFixedWidth(255-70)
            
            else:
                history_border.setGeometry(224+move-border_width, 50-border_width, 225+border_width*2, 50+border_width*2)
                history_selection.setGeometry(224+move, 50, 225, 50)


        clear_history_button.move(history_selection.x() + history_selection.width()-(clear_history_button.width() + 5), clear_history_button.y())
        
        info_button.move(info_button.x(), 10+resizeBorderWidth)
        about_button.move(about_button.x(), 10+resizeBorderWidth)
        # määritä asetusvalikon sijainnit resizeBorderWidth + backscreensmall.width() + 40

        contentMargin = 20
        mainPadding = 10
        buttonPadding = 5

        areaHeight = backScreen.height() - ToolBar.height()
        if ddx_on or solve_button_on:
            lineHeight = ddx_line.height() + mainPadding
        else:
            lineHeight = 0

        textEditPercentage = (areaHeight - copyButton.height()*2 - 4*mainPadding - contentMargin - 5 - lineHeight) / (areaHeight*2)

        x_offset = resizeBorderWidth + contentMargin

        pasteButton.setGeometry(x_offset, contentMargin + ToolBar.height(), (backScreenSmall.width()-contentMargin*2-mainPadding) // 2, pasteButton.height())
        quickButton.setGeometry(x_offset + pasteButton.width() + mainPadding, pasteButton.y(), pasteButton.width(), pasteButton.height())
        inputEdit.setGeometry(x_offset, pasteButton.y()+pasteButton.height()+mainPadding, backScreenSmall.width()-contentMargin*2, round(areaHeight * textEditPercentage))
        copyButtonHeight = copyButton.height()
        copyButton.setGeometry(x_offset, inputEdit.y()+inputEdit.height()+mainPadding, backScreenSmall.width()-contentMargin*2, copyButtonHeight)
        outputEdit.setGeometry(x_offset, copyButton.y()+copyButtonHeight+mainPadding, backScreenSmall.width()-contentMargin*2, round(areaHeight * textEditPercentage))

        if solve_button_on and ddx_on:
            variable_line.setGeometry(x_offset, outputEdit.y()+outputEdit.height()+mainPadding, quickButton.width(), quickButton.height())
            ddx_line.setGeometry(quickButton.x(), variable_line.y(), variable_line.width()-mainPadding-copyButtonHeight, variable_line.height())
            
        else:
            variable_line.setGeometry(variable_line.x(), outputEdit.y()+outputEdit.height()+mainPadding, copyButton.width(), copyButtonHeight)
            ddx_line.setGeometry(variable_line.x(), variable_line.y(), variable_line.width()-mainPadding-copyButtonHeight, copyButtonHeight)
        
        ddx_nth.setGeometry(ddx_line.x()+ddx_line.width()+mainPadding, ddx_line.y(), copyButtonHeight, copyButtonHeight)

        SumBorderBackScreen = resizeBorderWidth + backScreenSmall.width()

        buttonAreaWidth = backScreen.width() - backScreenSmall.width()
        textEditPercentage = (buttonAreaWidth - 0) / (buttonAreaWidth*2)

        buttonHeight = SC_button.height()
        button_x = SumBorderBackScreen + contentMargin
        SC_button.setGeometry(button_x, pasteButton.y(), buttonAreaWidth-2*contentMargin, buttonHeight)
        buttonWidth = SC_button.width()
        TI_button.setGeometry(button_x, SC_button.y()+buttonPadding+buttonHeight, buttonWidth, buttonHeight)

        constants_button.setGeometry(button_x, TI_button.y()+buttonPadding+buttonHeight, round(buttonWidth*(2/3)-2), buttonHeight)
        coulomb_button.setGeometry(button_x + constants_button.width()+6, constants_button.y(), round(buttonWidth*(1/3)-4), buttonHeight)

        e_button.setGeometry(button_x, constants_button.y()+buttonPadding+buttonHeight, round(buttonWidth*(1/3)-4), buttonHeight)
        i_button.setGeometry(button_x + e_button.width() + 6, e_button.y(), round(buttonWidth*(1/3)-4), buttonHeight)
        g_button.setGeometry(coulomb_button.x(), e_button.y(), coulomb_button.width(), buttonHeight)

        solve_button.setGeometry(button_x, e_button.y()+buttonPadding+buttonHeight, round(buttonWidth*(1/2)-2), buttonHeight)
        ddx.setGeometry(button_x + solve_button.width()+5, solve_button.y(), round(buttonWidth*(1/2)-3), buttonHeight)
        
        stay_on_top_button.setGeometry(button_x, solve_button.y()+buttonPadding+buttonHeight, buttonWidth, buttonHeight)

class InfoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About LaTeX2Calc")
        self.setWindowIcon(QIcon(dir_path + "\\rounded_logo_png.png"))
        self.setGeometry(100, 100, 500, 600)
        self.setMinimumSize(420, 300)

        layout = QVBoxLayout()

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setAlignment(Qt.AlignTop)

        image_label = QLabel(self)
        pixmap = QPixmap(dir_path + "\\rounded_logo_png.png")

        resize_factor = 0.5
        transform = QTransform().scale(resize_factor, resize_factor)
        resized_pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)

        image_label.setPixmap(resized_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(image_label)

        font = QFont()
        font.setPointSize(10)
        font.setBold(True)
        header_label = QLabel("LaTeX2Calc")
        header_label.setFont(font)
        header_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(header_label)
        
        text_label = QLabel("""v2.0.1
(PyQt5)
""")
        text_label.setAlignment(Qt.AlignCenter)
        text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        scroll_layout.addWidget(text_label)

        headerFont = QFont()
        font.setPointSize(8)
        headerFont.setBold(True)

        header = QLabel("Developer")
        header.setFont(font)
        header.setAlignment(Qt.AlignCenter)
        header.setTextInteractionFlags(Qt.TextSelectableByMouse)
        scroll_layout.addWidget(header)

        text_label2 = QLabel("""Johannes Ylinen
                             

This application utilizes the PyQt5 library
to provide its user interface and functionality."""
                            )
        text_label2.setAlignment(Qt.AlignCenter)
        text_label2.setTextInteractionFlags(Qt.TextSelectableByMouse)
        scroll_layout.addWidget(text_label2)


        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)

        layout.addWidget(scroll_area)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch(1)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        
        self.setLayout(layout)

class RoundedWidget(QWidget):
    def __init__(self, window, color, getAlpha=None, backgroundWidget=False):
        super().__init__(window)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.color = color
        self.getAlpha = getAlpha
        self.backgroundWidget = backgroundWidget

    def mousePressEvent(self, event):
        if self.backgroundWidget:
            self.mousePressEvent = lambda event: clearTextFocus()
        else:
            themeLine.clearFocus()
        pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(self.color))) # sel. def. col. "#0b0f13", win. "black"
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10,10)

    def setNewColor(self, color):
        colorComponents = getColorComponents(color)
        
        if colorComponents:
            red, green, blue, alpha = colorComponents
            if self.getAlpha:
                if 'alphaSlider' in globals():
                    alpha = alphaSlider.value()
            self.color = QColor(red, green, blue, alpha)
            self.update()
        else:
            color = QColor(color)
            red, green, blue, alpha = color.getRgb()
            if self.getAlpha:
                if 'alphaSlider' in globals():
                    alpha = alphaSlider.value()
            self.color = QColor(red, green, blue, alpha)
            self.update()

class RoundedWidgetBorder(QWidget):
    def __init__(self, window, color, *args, **kwargs):
        super().__init__(window, *args, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.color = color

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(self.color))) #192328
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.rect(), 10,10)

    def mousePressEvent(self, event):
        themeLine.clearFocus()
        pass

    def setNewColor(self, color):
        colorComponents = getColorComponents(color)
        if colorComponents:
            red, green, blue, alpha = colorComponents
            self.color = QColor(red, green, blue, alpha)
            self.update()
        else:
            self.color = QColor(color)
            self.update()

class textEdit(QTextEdit):
    def __init__(self, window, x, y, width, height, name=None):
        super().__init__(window)
        self.move(x, y)
        self.resize(width, height)
        self.setTabStopWidth(20)
        self.setAcceptRichText(False)
        if name == "inputEdit":
            self.textChanged.connect(translate_input)

    def mousePressEvent(self, event):
        close_selection()
        super().mousePressEvent(event)

    def addStyle(self, style, text):
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setStyleSheet(style)
        self.setLineWrapMode(QTextEdit.WidgetWidth)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setPlaceholderText(text)

class lineEdit(QLineEdit):
    def __init__(self, window, x, y, width, height, closeSelection=True, name=None):
        super().__init__(window)
        self.move(x, y)
        self.resize(width, height)
        self.name = name
        if self.name != "themeLine":
            self.textChanged.connect(translate_input)
        self.closeSelection = closeSelection

        if closeSelection and (info_on or theme_on or history_list_on):
            self.mousePressEvent = lambda event: close_selection()

    def addStyle(self, style, text):
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(style)
        self.setPlaceholderText(text)

class button(QPushButton):
    buttons = []
    def __init__(self, window, pos, width, height, text):
        super().__init__(text, window)
        button.buttons.append(self)
        self.move(pos[0], pos[1])
        self.resize(width, height)
        self.setFont(QFont("", 14))
        
    def mousePressEvent(self, event):
        close_selection()
        super().mousePressEvent(event)

    def addStyle(self, style):
        self.setStyleSheet(style)
        self.setCursor(Qt.PointingHandCursor)

class IgnoringButton(QPushButton):
    def __init__(self, window, pos, width, height, text, ignore=False):
        super().__init__(text, window)
        self.move(pos[0], pos[1])
        self.resize(width, height)
        self.setFont(QFont("", 14))
        self.ignore = ignore
        
    def mousePressEvent(self, event):
        if self.ignore:
            clear_history()
            self.move(history_selection.x() + history_selection.width()-(clear_history_button.width() + 5), clear_history_button.y())
            pass
        else:
            close_selection()
            super().mousePressEvent(event)


    def addStyle(self, style):
        self.setStyleSheet(style)
        self.setCursor(Qt.PointingHandCursor)

class IgnoringLabel(QLabel):
    def mousePressEvent(self, event):
        themeLine.clearFocus()
        pass

class ToolButton(QPushButton):
    def __init__(self, window, pos, width, height, text, colorButton=False):
        super().__init__(text, window)
        self.move(pos[0], pos[1])
        self.resize(width, height)
        self.setFont(QFont("", 14))
        self.setCursor(Qt.PointingHandCursor)
        if colorButton:
            self.clicked.connect(self.change_color)
    
    def change_color(self):
        new_color = QColorDialog.getColor(QColor(255,255,255), window, "Select Color")
        if new_color.isValid():
            themeLine.setText(f'rgb({new_color.red()},{new_color.green()},{new_color.blue()})')
            getCustomColor(presetColor=new_color)

    def addStyle(self, style):
        self.setStyleSheet(style)

class textArea(QLabel):
    def __init__(self, window, text, x, y, style, fontSize=None):

        super().__init__(text, window)
        self.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  
        self.move(x, y)
        self.setStyleSheet(style)
        if fontSize is not None:
            font = QFont()
            font.setPointSize(fontSize)
            self.setFont(font)
        
    def mousePressEvent(self, event):
        pass

class DraggableWidget(QWidget):
    def __init__(self, window):
        super().__init__(window)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(0, 255, 0))
        self.setPalette(palette)
        self.dragPos = QPoint(0, 0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.window().frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.window().move(event.globalPos() - self.dragPos)
            event.accept()

class CheckBox(QCheckBox):
    def __init__(self, text, window):
        super().__init__(text, window)
        self.setCursor(Qt.PointingHandCursor)

    def addStyle(self, style):
        self.setStyleSheet(style)

class Slider(QSlider):
    def __init__(self, window, x, y, width, height, sliderStartValue=128):
        super().__init__(window)
        self.setOrientation(Qt.Horizontal)
        self.setGeometry(x, y, width, height)
        self.setMinimum(0)
        self.setMaximum(255)
        self.setValue(sliderStartValue)
        self.label_x = x-7
        self.label_y = y + height

        # Add a label to display the current value
        self.label = IgnoringLabel(window)
        self.label.setGeometry(self.label_x, self.label_y, width+20, height)
        self.label.setStyleSheet("color: white")

        # Connect the valueChanged signal to the custom function
        self.valueChanged.connect(self.getSliderValue)
        self.valueChanged.connect(updateBackScreen)

    def getSliderValue(self, value):
        offSet = 4 * (3 - len(str(value)))
        self.label.move(self.label_x + offSet, self.label_y)
        self.label.setText(f"Background opacity: {value}")

    def addStyle(self, handleColor, grooveColor):
        self.setStyleSheet(
            "QSlider::groove:horizontal {"
            "    height: 20px;"
            "    background-color: " + grooveColor + ";"  # Change the background color of the slider
            "    border: 2px solid " + handleColor + ";"
            "    border-radius: 3px;"
            "}"

            "QSlider::handle:horizontal {"
            "    width: 20px;"
            "    height: 20px;"
            "    background-color: " + handleColor + ";"  # Change the handle color
            "    border-radius: 3px;"
            "}"
            )

class HistoryButton(QPushButton):
    def __init__(self, text, value):
        super().__init__(text)
        self.value = value

class ScrollClass(QWidget):
    global history
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.initUI()

    def mousePressEvent(self, event):
        pass

    def formatText(self, button):
        maxCharPerRow = round(self.width() / 220 * 18)
        text = button.text()
        text = text.replace(" ", "").replace("\n", "")
        formatted_text = '\n'.join([text[i:i+maxCharPerRow] for i in range(0, len(text), maxCharPerRow)])
        newLineCount = formatted_text.count("\n")
        button.setText(formatted_text)
        
        button.setFixedHeight((newLineCount + 1) * (self.fontSize+12))
        return newLineCount

    def initUI(self):
        self.setGeometry(230+move, 50, 210, 360)

        # Create a scroll area widget
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollArea.setFrameShape(QFrame.NoFrame)
        self.fontSize = 14

        self.maxCharPerRow = round(self.width() / 220 * 18)

        self.scrollHeight = 0 # POISTA
        for latex, translation in history.items():
            self.scrollHeight += ((len(translation) + (self.maxCharPerRow - 1)) // self.maxCharPerRow) * (self.fontSize+10) + 20
        if 40 + self.scrollHeight < 200:
            self.scrollArea.setMinimumSize(210, self.scrollHeight)
        else:
            self.scrollArea.setMaximumHeight(360)

        self.scrollArea.setStyleSheet("background-color: transparent;")

        # Create a widget to contain the buttons
        self.buttonsWidget = QWidget()
        self.scrollArea.setWidget(self.buttonsWidget)
        
        def on_button_clicked(button):
            button_text = button.text()
            button_text = button_text.replace(" ", "").replace("\n", "")

            inputEdit.setText(button.value)
            outputEdit.setText(button_text)
            translate_input()

        # Create a vertical layout for the buttons
        buttonsLayout = QVBoxLayout(self.buttonsWidget)
        buttonsLayout.setAlignment(Qt.AlignTop)

        def reverse_dictionary(d):
            keys = list(d.keys())
            values = list(d.values())
            keys.reverse()
            values.reverse()
            return {k: v for k, v in zip(keys, values)}

        reverseHistory = reverse_dictionary(history)

        for latex, translation in reverseHistory.items():
            translation = '\n'.join([translation[i:i+self.maxCharPerRow] for i in range(0, len(translation), self.maxCharPerRow)])
            rows = (len(translation) + (self.maxCharPerRow - 1)) // self.maxCharPerRow
            button = HistoryButton(translation, latex)
            self.formatText(button)
            self.buttons.append(button)

            button.setFixedSize(192, rows*(self.fontSize + 10) + 20)
            button.setFont(QFont("", self.fontSize))
            button.setStyleSheet("text-align:left; vertical-align:top; background-color: transparent")
            button.setCursor(Qt.PointingHandCursor)
            buttonsLayout.addWidget(button)
            button.clicked.connect(lambda checked, button=button: on_button_clicked(button))

    def updateScrollClass(self):
        buttonsHeight = 6*2+10
        for button in self.buttons:
            buttonsHeight += button.height() + 5

        if buttonsHeight > window.height()-ToolBar.height()-30:
            self.setFixedSize(history_selection.width()-10, window.height() - ToolBar.height()-30)
            self.scrollArea.setFixedSize(self.width(), self.height())
        else:
            self.setFixedSize(history_selection.width()-10, buttonsHeight)
            self.scrollArea.setFixedSize(self.width(), self.height())

        for button in self.buttons:
            button.setFixedWidth(self.width()-30)
            self.formatText(button)

app = QApplication(sys.argv)

screen_resolution = getScreenRes()
resizeBorderWidth = 10
windowSplitFactor = (440-15)/(670)
window = MainWindow("black", resizeBorderWidth)
window.setWindowTitle("LaTeX2Calc")
window.setMinimumSize(550, 410)
window.setGeometry(0, 0, windowDimensions[0], windowDimensions[1])
if windowPos:
    window.move(windowPos)
else:
    positionWindow(window)

backScreen = RoundedWidget(window, "black", True, True)
backScreen.setGeometry(window.rect().adjusted(1, 1, -1, -1))
backScreenSmall = RoundedWidget(window, "black", True, True)

window.stackUnder(backScreen)
backScreenSmall.stackUnder(backScreen)
    
# load images
def load_and_process_image(file_path, target_width, target_height):
    return QPixmap(file_path).scaled(target_width, target_height)

def create_rounded_pixmap(img, radius):
    rounded = QtGui.QPixmap(img.size())
    rounded.fill(QtGui.QColor("transparent"))

    painter = QtGui.QPainter(rounded)
    # painter.setRenderHint(QtGui.QPainter.Antialiasing)
    painter.setBrush(QtGui.QBrush(img))
    painter.setPen(QtCore.Qt.NoPen)
    painter.drawRoundedRect(img.rect(), radius, radius)
    
    return rounded

def create_and_configure_label(parent, pixmap, x, y, width, height, visible=True):
    label = QLabel(parent)
    label.setPixmap(pixmap)
    label.setGeometry(x, y, width, height)
    if not visible:
        label.hide()
    return label

dir_path = os.path.dirname(os.path.abspath(__file__))
radius = 10
border_width = 1 

# Show window icon
window.setWindowIcon(QIcon(dir_path + "\\rounded_logo_png.png"))

# create buttons and text areas
inputEdit = textEdit(window, 20, 125, 400, 100, "inputEdit")
inputEdit.addStyle(text_edit_style, text=" LATEX")

outputEdit = textEdit(window, 20, 290, 400, 100)
outputEdit.addStyle(text_edit_style, text=" TRANSLATION")

variable_line = lineEdit(window, 20, 400, 400, 40)
variable_line.addStyle(text_edit_style, "Solve variable(s) | condition")
variable_line.hide()

ddx_line = lineEdit(window, 20, 400, 350, 40)
ddx_line.addStyle(text_edit_style, "Differentiation variable")
ddx_line.hide()

ddx_nth = lineEdit(window, 380, 400, 40, 40)
ddx_nth.addStyle(text_edit_style, "nth")
ddx_nth.hide()

pasteButton = button(window, (20, 70), width=196, height=45, text="Paste LaTeX")
pasteButton.addStyle(style=buttonStyle)

quickButton = button(window, (225, 70), width=196, height=45, text="Quick Translate")
quickButton.addStyle(style=buttonStyle)

copyButton = button(window, (20, 235), width=400, height=45, text="Copy")
copyButton.addStyle(style=buttonStyle)


SC_button = button(window, (460, 70), width=190, height=45, text="SpeedCrunch")
SC_button.addStyle(style=toggle_button_off_style)

TI_button = button(window, (460, 120), width=190, height=45, text="TI")
TI_button.addStyle(toggle_button_on_style)

constants_button = button(window, (460, 170), width=190-61-4, height=45, text="Contants")
constants_button.addStyle(toggle_button_off_style)

coulomb_button = button(window, (589, 170), width=61, height=45, text="Cc")
coulomb_button.addStyle(toggle_button_off_style)

e_button = button(window, (460, 220), width=61, height=45, text="e")
e_button.addStyle(toggle_button_off_style)

i_button = button(window, (525, 220), width=60, height=45, text="i")
i_button.addStyle(toggle_button_off_style)

g_button = button(window, (460+64*2+1, 220), width=61, height=45, text="g")
g_button.addStyle(toggle_button_off_style)

solve_button = button(window, (460, 270), width=95-2, height=45, text="Solve")
solve_button.addStyle(toggle_button_off_style)

ddx = button(window, (557, 270), width=95-2, height=45, text="dⁿ/dxⁿ")
ddx.addStyle(toggle_button_off_style)

stay_on_top_button = button(window, (460, 320), width=190, height=45, text="Stay on top")
stay_on_top_button.addStyle(toggle_button_off_style)

ToolBar = QFrame(window)
ToolBar.setStyleSheet(tool_bar_style)

draggableBar = DraggableWidget(window)
draggableBar.setGeometry(0, 0, 800, 55)

move = -20-92
info_border = RoundedWidgetBorder(window, color="#192328")
info_border.setGeometry(319+move-border_width, 50-border_width, 322+border_width*2, 350+border_width*2)
info_border.hide()

info_page = RoundedWidget(window, color="0b0f13")
info_page.setGeometry(319+move, 50, 322, 350)
info_page.hide()

fontStyle = "background-color: transparent; color: white; font-size: 25px;"

header_x = 326+move
header_y = 55
header_text = textArea(window, "Shortcuts", header_x, header_y, fontStyle)
header_text.hide()

fontStyle = "background-color: transparent; color: white; font-size: 10"
text = "Ctrl + Q\nCtrl + P\nCtrl + Shift + C\nCtrl + S\nCtrl + T\nCtrl + K\nCtrl + L\nCtrl + E\nCtrl + I\nCtrl + G\nCtrl + Shift + S\nCtrl + D\nCtrl + H\nShift + Alt + R"

info_x = header_x + 5
info_y = header_y + 30
info_text = textArea(window, text, info_x, info_y, fontStyle, fontSize=9)
info_text.hide()

action_x = info_x + 155
action_y = info_y 
text = "Quick translate\nPaste\nCopy\nSpeedCrunch\nTI-nspire\nConstants\nCoulomb const.\nTI e symbol\nTI i symbol\nTI gravity\nSolve\nd/dx\nStay on top\nReset (restart req.)"
action_text = textArea(window, text, info_x + 155, info_y, fontStyle, fontSize=9)
action_text.hide()

theme_button = ToolButton(window, (132+move,10), width=90, height=35, text="Theme")
theme_button.addStyle(selection_off_style)

theme_selection_border = RoundedWidgetBorder(window, color="#192328")
theme_selection_border.setGeometry(132+move-border_width, 50-border_width, 200+border_width*2, 85+border_width*2 + 150)
theme_selection_border.hide()

theme_selection = RoundedWidget(window, color="0b0f13")
theme_selection.setGeometry(132+move, 50, 200, 85 + 150)
theme_selection.hide()

themeLine = lineEdit(window, 152+move, 60, 160, 30, closeSelection=False, name="themeLine")
themeLine.addStyle("background-color: rgba(0,0,0,30); color: white; border-bottom: 1.5px solid white; border-radius: 0px", "HEX, RGB, COLOR" )

if userInputColor:
    themeLine.setText(userInputColor)
themeLine.hide()

light_mode = CheckBox("Light mode", window)
light_mode.setGeometry(172+move, 90, 115, 40)
light_mode.addStyle(checkbox_style)
if inverse_theme:
    light_mode.setChecked(True)
light_mode.hide()

transparent_window = CheckBox("Transparent\n  window", window) 
transparent_window.setGeometry(172+move, 135, 120, 40)
transparent_window.addStyle(checkbox_style)
if transparentWindowState:
    transparent_window.setChecked(True)
transparent_window.hide()

colorButton = ToolButton(window, (147+move, 235), width=170, height=40, text="More colors", colorButton=True)
colorButton.setFont(QFont("", 14))
colorButton.addStyle(buttonStyle + "QPushButton {background-color: rgba(0,0,0,0); color: rgba(255,255,255,200);};")
colorButton.hide()

history_button = ToolButton(window, (224+move,10), width=90, height=35, text="History")
history_button.addStyle(selection_off_style)

history_border = RoundedWidgetBorder(window, color="#192328")
history_border.setGeometry(224+move-border_width, 50-border_width, 225+border_width*2, 100+border_width*2)
history_border.hide()

history_selection = RoundedWidget(window, color="0b0f13")
history_selection.setGeometry(224+move, 50, 225, 100)
history_selection.hide()

history_x = 246+move
history_y = 62
history_text = textArea(window, "No history", history_x, history_y, style="background-color: transparent; color: white;", fontSize=10)
history_text.hide()

clear_history_button = IgnoringButton(window, (history_x+138, history_y-5), width=58, height=35, text="Clear", ignore=True)
clear_history_button.addStyle(selection_off_style + "QPushButton {background-color: rgba(0, 0, 0, 200)}")
clear_history_button.hide()

info_button = ToolButton(window, (316+move,10), width=35, height=35, text="🛈")
info_button.addStyle(selection_off_style + "QPushButton {font-size: 30px; }")

about_button = ToolButton(window, (353+move,10), width=66, height=35, text="About")
about_button.addStyle(selection_off_style)

minimize_button = button(window, (560, -5), width=55, height=55, text="‒")
minimize_button.setFont(QFont("", 30))
minimize_button.addStyle(close_buttonStyle)

close_button = button(window, (615, 0), width=55, height=55, text="×")
close_button.setFont(QFont("", 30))
close_button.addStyle(close_buttonStyle)

alphaSlider = Slider(window, 152+move, 185, 160, 24, sliderStartValue=sliderStartValue)
alphaSlider.addStyle("#0078d4", "#dddddd")
alphaSlider.getSliderValue(alphaSlider.value())
alphaSlider.hide()
alphaSlider.label.hide()

# set buttons actions
stay_on_top_button.clicked.connect(toggle_stay_on_top)
SC_button.clicked.connect(SC_button_clicked)
TI_button.clicked.connect(TI_button_clicked)
constants_button.clicked.connect(constants_button_clicked)
coulomb_button.clicked.connect(coulomb_button_clicked)
e_button.clicked.connect(e_button_clicked)
i_button.clicked.connect(i_button_clicked)
g_button.clicked.connect(g_button_clicked)
quickButton.clicked.connect(on_quick_button_clicked)
copyButton.clicked.connect(copy_to_clipboard)
solve_button.clicked.connect(solve_button_clicked)
ddx.clicked.connect(ddx_clicked)
pasteButton.clicked.connect(paste_clipboard_text)
history_button.clicked.connect(history_list_clicked)
theme_button.clicked.connect(theme_selection_clicked)
info_button.clicked.connect(info_button_clicked)
about_button.clicked.connect(about_button_clicked)
close_button.clicked.connect(lambda: saveSettings(windowClosed=True))
minimize_button.clicked.connect(window.showMinimized)

# shortcuts
shortcut_mappings = {
    Qt.CTRL + Qt.Key_Q: on_quick_button_clicked,
    Qt.CTRL + Qt.Key_P: paste_clipboard_text,
    Qt.CTRL + Qt.SHIFT + Qt.Key_C: copy_to_clipboard,
    Qt.CTRL + Qt.Key_T: TI_button_clicked,
    Qt.CTRL + Qt.Key_K: constants_button_clicked,
    Qt.CTRL + Qt.Key_L: coulomb_button_clicked,
    Qt.CTRL + Qt.Key_S: SC_button_clicked,
    Qt.CTRL + Qt.Key_E: e_button_clicked,
    Qt.CTRL + Qt.Key_I: i_button_clicked,
    Qt.CTRL + Qt.Key_G: g_button_clicked,
    Qt.CTRL + Qt.SHIFT + Qt.Key_S: solve_button_clicked,
    Qt.CTRL + Qt.Key_D: ddx_clicked,
    Qt.CTRL + Qt.Key_H: toggle_stay_on_top,
    Qt.SHIFT + Qt.ALT + Qt.Key_R: reset_settings
}

for key_sequence, function in shortcut_mappings.items():
    shortcut = QShortcut(QKeySequence(key_sequence), window)
    shortcut.activated.connect(function)
    
# save settings
def saveSettings(windowClosed=False):
    global SC_on, TI_on, e_on, i_on, g_on, stay_on_top_on, solve_button_on, ddx_on, theme_on, history_list_on
    global info_on, constants_on, coulomb_on, inverse_theme, transparentWindowState

    settings_manager = SettingsManager()

    # Create a dictionary to store variable names and values

    variables_to_save = {

        # settings
        "SC_on": SC_on,
        "TI_on": TI_on,
        "e_on": e_on,
        "i_on": i_on,
        "g_on": g_on,
        "stay_on_top_on": stay_on_top_on,
        "solve_button_on": solve_button_on,
        "ddx_on": ddx_on,
        "constants_on": constants_on,
        "coulomb_on": coulomb_on,

        # theme
        "inverse_theme": inverse_theme,
        "transparentWindowState": transparentWindowState,
        "userInputColor": themeLine.text(),
        "sliderStartValue": alphaSlider.value(),

        # history
        "history": history,
        "historyLen": historyLen
    }

    # Save variables using the settings_manager
    for variable_name, variable_value in variables_to_save.items():
        settings_manager.save_variable(variable_name, variable_value)


    if (window.x() > 0 and
        window.x() < screen_resolution[0] - window.width() and
        window.y() > 0 and
        window.y() < screen_resolution[1] - window.height()
    ):
        settings_manager.save_variable("windowPos", window.pos())
        settings_manager.save_variable("windowDimensions", (window.width(), window.height()))

    if windowClosed:
        if hasattr(window, 'info_window'):
            window.info_window.close()
        window.close()

inverseColors(inverse_theme)
getCustomColor()

def changeTheme():
    if themeLine.text() == '':
        applyDefaultTheme()
    
    saveSettings()
    inverseColors(inverse_theme)
    getCustomColor()

# finish loading settings
translate_input()

themeLine.textChanged.connect(changeTheme)
light_mode.stateChanged.connect(inverseTheme)
transparent_window.stateChanged.connect(changeWindowState)
updateInverse()


# show main window
window.show()
sys.exit(app.exec_())