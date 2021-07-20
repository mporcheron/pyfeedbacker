# -*- coding: utf-8 -*-

from pyfeedbacker.app import stage



class StageIsgood(stage.HandlerForm):
    pass

    # This is a dynamic stage that is handled entirely by the configuration
    # and the UI (i.e., the configuration specifies the form options and the
    # UI draws that).

    # The stage handler (HandlerForm) auto generates the appropriate outcomes
    # and information for the UI from the configuration, passing an OutputForm
    # object to the view. This uses an adapter (AdapterForm) to convert this
    # into UI elements. 