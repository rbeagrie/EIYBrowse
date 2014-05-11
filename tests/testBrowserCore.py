from browser.core import Browser
from browser.panels.base import Panel
from mock import Mock, patch, call
from pybedtools import Interval

test_feature = Interval('chr1',0,1)

def test_plot_calls_panel_config():
    browser = Browser()
    panel = Panel()
    panel.get_config = Mock(return_value={'lines':1})
    browser.panels.append(panel)
    browser.plot(test_feature)
    panel.get_config.assert_called_with(test_feature)

def test_plot_calls_browser_getaxes():
    browser = Browser()
    browser.get_axes = Mock(return_value=[])
    browser.plot(test_feature)
    browser.get_axes.assert_called_with([])

@patch('browser.core.plt.figure')
def test_one_panel_figure_correct_size(mock_figure):
    browser = Browser()
    browser.get_axes([{'lines':2}])
    mock_figure.assert_called_with(figsize=(16,1.0))

@patch('browser.core.plt.figure')
def test_two_panel_figure_correct_size(mock_figure):
    browser = Browser()
    browser.get_axes([{'lines':2}, {'lines':4}])
    mock_figure.assert_called_with(figsize=(16,3.0))

@patch('browser.core.plt.subplot2grid')
def test_one_panel_axes_correct(mock_subplot):
    browser = Browser()
    browser.get_axes([{'lines':2}])
    mock_subplot.assert_called_with((2, 1), (0, 0), rowspan=2)

@patch('browser.core.plt.subplot2grid')
def test_two_panel_axes_correct(mock_subplot):
    browser = Browser()
    browser.get_axes([{'lines':2}, {'lines':4}])
    calls = [call((6, 1), (0, 0), rowspan=2),
             call((6, 1), (2, 0), rowspan=4),]
    mock_subplot.assert_has_calls(calls)
    
