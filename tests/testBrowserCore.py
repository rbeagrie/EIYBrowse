from browser.core import Browser
from browser.panels.base import Panel
from mock import Mock
from pybedtools import Interval

def test_plot_calls_panel_config():
    browser = Browser()
    panel = Panel()
    panel.get_config = Mock(return_value={'lines':1})
    browser.panels.append(panel)
    feature = Interval('chr1',0,1)
    browser.plot(feature)
    panel.get_config.assert_called_with(feature)

