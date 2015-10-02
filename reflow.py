'''
Copyright (C) 2015 Diego Gangl
diego@sinestesia.co

Created by Diego Gangl

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy
import bpy.props as prop
import re

class KS_OT_Reflow(bpy.types.Operator):
    bl_idname = "keys.reflow"
    bl_label = "Reflow"
    bl_description = "Recalculate animations for a different fps"
    bl_options = {"REGISTER", "UNDO"}
    

    fps_source = prop.IntProperty(
                                   name = "Source FPS",
                                   min = 1,
                                   default = self.default_source_fps,
                                   description = "Original FPS to convert from"
                                 )
    

    fps_dest = prop.IntProperty(
                                 name = "Destination FPS",
                                 min = 1,
                                 default = 60,
                                 description = "Final FPS to convert to"
                               )
    
    @classmethod
    def poll(cls, context):
        return len(bpy.data.actions) > 0


    def default_source_fps(self):
        return bpy.context.scene.render.fps
    
    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)


    def keyframe_resample(self, curve):
        """ Resample every keyframe in a curve """
        
        for keyframe in curve.keyframe_points:
            frame_original = keyframe.co[0]

            if frame_original != 0:
                keyframe.co[0] = frame_original // self.diff



    def fix_nla_length(self, track):
        """ Fix start and end frames for NLA tracks """

        for strip in track.strips:
            strip.action_frame_start //= self.diff
            strip.action_frame_end //= self.diff


    
    def execute(self, context):

        render = context.scene.render

        actions = bpy.data.actions
        markers = context.scene.timeline_markers
        objects = bpy.data.objects

        # Tomar diff
        self.diff = self.fps_source / self.fps_dest

        # Setear fps destino
        render.fps = fps_dest


        # Loopear por cada accion
        for action in actions:
            for curve in action.fcurves:
                self.keyframe_resample(curve)    



        # Arreglar tracks NLA
        # Los tracks van por objeto
        for obj in objects:
            if obj.animation_data and obj.animation_data.use_nla:
                for track in obj.animation_data.nla_tracks:
                    self.fix_nla_length(track)


        # Loopear cada marker
        for mark in markers:
            if mark.frame != 0:
                new_frame = mark.frame // diff
                mark.frame = new_frame

                regex = re.match('^F_[0-9]*$', mark.name)

                if regex:
                    mark.name = 'F_{0}'.format(new_frame)


        

        
        return {'FINISHED'}
