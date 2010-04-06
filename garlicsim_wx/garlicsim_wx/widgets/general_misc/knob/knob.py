from __future__ import division

import wx
import math
import pkg_resources
from garlicsim.general_misc import math_tools
from garlicsim_wx.general_misc import wx_tools
from garlicsim_wx.general_misc import cursor_collection
from garlicsim.general_misc import binary_search
from garlicsim.general_misc import cute_iter_tools
from . import images as __images_package
images_package = __images_package.__name__



class Knob(wx.Panel):
    def __init__(self, parent, getter, setter, *args, **kwargs):
        
        assert 'size' not in kwargs
        
        assert callable(setter) and callable(getter)
        self.value_getter, self.value_setter = getter, setter
        
        wx.Panel.__init__(self, parent, *args, size=(30, 30), **kwargs)
        
        self.original_bitmap = wx.Bitmap(
            pkg_resources.resource_filename(images_package, 'knob.png'),
            wx.BITMAP_TYPE_ANY
        )
        
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.on_mouse)
        
        self.SetCursor(cursor_collection.get_open_grab())
        
        self.recalculation_flag = False        
        
        self.sensitivity = 25
        self.angle_resolution = math.pi / 180 # One degree
        self.current_angle = 0
        self.current_ratio = 0
        self.snap_points = []
        self.snap_point_ratio_well = 0.1
        
        self.base_drag_radius = 500 # in pixels
        self.snap_point_drag_well = \
            self.snap_point_ratio_well * self.base_drag_radius
        
        self.being_dragged = False
        
        self.grabbed_y = None
        self.grabbed_ratio = None
        self.origin_y_while_dragging = None
        self.snap_points_y_starts = []
        #self.ratio_while_dragging = None
        #self.d_angle_while_dragging = None
        #self.desired_clock_while_dragging = None
        
    def _angle_to_ratio(self, angle):
        return angle / (math.pi * 5 / 6)

    def _ratio_to_value(self, ratio):
        #return self.sensitivity * \
               #math_tools.sign(ratio) * \
               #(-2*math.log(math.cos((math.pi*ratio)/2))) / math.pi
        return self.sensitivity * \
               math_tools.sign(ratio) * \
               (4 / math.pi**2) * \
               math.log(math.cos(ratio * math.pi / 2))**2
        
    def _value_to_ratio(self, value):
        return math_tools.sign(value) * \
               (2 / math.pi) * \
               math.acos(
                   math.exp(
                       - (math.pi * math.sqrt(abs(value))) / \
                       (2 * math.sqrt(self.sensitivity))
                   )
               )

    def _ratio_to_angle(self, ratio):
        return ratio * (math.pi * 5 / 6)
    
    
    def set_snap_point(self, value):
        # Not optimizing with the sorting for now
        self.snap_points.append(value)
        self.snap_points.sort()
    
    def remove_snap_point(self, value):
        self.snap_points.remove(value)
        
    def _recalculate(self):
        value = self.value_getter()
        self.current_ratio = self._value_to_ratio(value)
        angle = self._ratio_to_angle(self.current_ratio)
        d_angle = angle - self.current_angle
        if abs(d_angle) > self.angle_resolution:
            self.current_angle = angle
            self.Refresh()
        self.recalculation_flag = False
    
    def on_paint(self, event):
        event.Skip()
        if self.recalculation_flag:
            self._recalculate()
        
        dc = wx.PaintDC(self)

        w, h = self.GetClientSize()
        
        wx_tools.draw_bitmap_to_dc_rotated(
            dc,
            self.original_bitmap,
            -self.current_angle,
            (w/2, h/2),
            useMask=True
        )
        
    def _get_snap_points_as_ratios(self):
        return [self._value_to_ratio(value) for value in self.snap_points]
    
    def __make_snap_points_y_starts(self):
        
        self.snap_points_y = []
        snap_point_ratios = self._get_snap_points_as_ratios()
        if not snap_point_ratios:
            return
        assert len(snap_point_ratios) >= 1
        my_i = binary_search.binary_search_by_index(
            snap_point_ratios,
            cmp,
            0,
            'low'
        )
        

        if my_i is None:
            first_positive_i = 0
        else:
            first_positive_i = my_i + 1
        
            if snap_point_ratios[my_i] == 0:
                first_negative_i = my_i - 1
                zero_is_snap_point = True
            else:
                first_negative_i = my_i
                zero_is_snap_point = False
            
        try:
            assert snap_point_ratios[first_negative_i] < 0
        except IndexError:
            pass
        
        try:
            assert snap_point_ratios[first_positive_i] > 0
        except IndexError:
            pass
        
                
            
        zero_padding = \
            self.snap_point_drag_well / 2 if zero_is_snap_point else 0

        negative_snap_point_ratio = snap_point_ratios[:first_negative_i+1]
        positive_snap_point_ratio = snap_point_ratios[first_positive_i:]
        
        
        
        for (i, ratio) in cute_iter_tools.enumerate(negative_snap_point_ratio,
                                                    reverse_index=True):
            assert ratio < 0 # todo: remove
            padding_to_add = i * self.snap_point_drag_well + zero_padding
            self.snap_points_y.append(
                ratio * self.base_drag_radius + padding_to_add
            )
        
        for (i, ratio) in enumerate(positive_snap_point_ratio):
            assert ratio > 0 # todo: remove
            padding_to_add = i * self.snap_point_drag_well + zero_padding
            self.snap_points_y.append(
                ratio * self.base_drag_radius + padding_to_add
            )
        
            
    def __get_snap_points_y_starts_from_origin(self, y):
        return [y_start for y_start in self.snap_points_y_starts
                if (0 <= y_start < y) or (0 >= y_start > 0)]
    
    def __get_n_snap_points_from_origin(self, ratio):
        '''note it returns a float'''
        snap_point_ratios = self._get_snap_points_as_ratios()
        snap_points_between = (s for s in snap_point_ratios if
                               (0 < s < ratio) or (0 > s > ratio))
        result = float(len(list(snap_points_between)))
        if any(s == 0 for s in snap_point_ratios):
            result += 0.5
        if any(s == ratio for s in snap_point_ratios):
            result += 0.5
            
    
    def __raw_map_y_to_ratio(self, y):
        assert self.being_dragged
        ratio = (y - self.origin_y_while_dragging) / self.base_drag_radius
        if abs(ratio) > 1:
            ratio = math_tools.sign(ratio)
        return ratio
    
    def __map_y_to_ratio(self, y):
        #raw_ratio = self.__raw_map_y_to_ratio(y)
        #self.__get_n_snap_points_from_origin(raw_ratio) * \
            #self.snap_point_drag_well()
        y_starts_from_origin = self.__get_snap_points_y_starts_from_origin(y)
        ry = y - self.grabbed_y
        padding_counter = 0
        
        if y_starts_from_origin[0] == 0:
            padding_counter += self.snap_point_drag_well / 2
            y_starts_from_origin.pop(0)
            
        distance_from_last = ry - y_starts_from_origin[-1]
        if distance_from_last < self.snap_point_drag_well:
            padding_counter += distance_from_last
            y_starts_from_origin.pop(-1)
        
        padding_counter += self.snap_point_drag_well * len(y_starts_from_origin)
        
        new_ry = ry - padding_counter
        assert math_tools.sign(new_ry) == math_tools.sign(ry)
        
        ratio = new_ry / self.snap_point_drag_well
        
        return ratio
        
    def on_mouse(self, event):
        # todo: maybe right click should give context menu with 'Sensitivity...'
        # todo: make check: if left up and has capture, release capture

        self.Refresh()
        
        (w, h) = self.GetClientSize()
        (x, y) = event.GetPositionTuple()
        (rx, ry) = (x/w, y/h)
        
        if event.LeftDown():
            self.being_dragged = True
            self.grabbed_y = y
            self.origin_y_while_dragging = y - \
                (self.base_drag_radius * (self.current_ratio + \
                self.snap_point_ratio_well * \
                self.__get_n_snap_points_from_origin(self.current_ratio)))
            self.__make_snap_points_y_starts()
            
            self.CaptureMouse()    
            self.SetCursor(cursor_collection.get_closed_grab())
            return
        
        if event.LeftIsDown() and self.HasCapture():
            ratio = self.__map_y_to_ratio(y)
            self.value_setter(ratio)
            
                
        if event.LeftUp() or (event.LeftIsUp() and self.HasCapture()):
            # todo: make sure that when leaving
            # entire app, things don't get fucked
            if self.HasCapture():
                self.ReleaseMouse()
            self.SetCursor(cursor_collection.get_open_grab())
            self.being_dragged = False
            self.grabbed_y = None
            self.grabbed_ratio = None
            self.origin_y_while_dragging = None
            del self.snap_points_y_starts[:]
            
            
        return
        
        
        
        
        
        
        
        
        
        