"""
Arranges clips onto the Premiere Sequence.
"""
import logging
from typing import List
from core.models.premiere_models import SequenceInfo, TimelineClip
from engines.premiere_engine.bridge.premiere_bridge import PremiereBridge
from core.exceptions.premiere_exceptions import TimelineError

logger = logging.getLogger(__name__)

class TimelineBuilder:
    """Takes abstract clip data and places it onto a specific sequence."""
    def __init__(self, bridge: PremiereBridge) -> None:
        self.bridge = bridge

    def build_timeline(self, sequence: SequenceInfo, clips: List[TimelineClip]) -> None:
        logger.info(f"Building XML timeline '{sequence.name}' with {len(clips)} clips.")
        try:
            import xml.etree.ElementTree as ET
            
            xmeml = ET.Element('xmeml', version='4')
            project = ET.SubElement(xmeml, 'project')
            name = ET.SubElement(project, 'name')
            name.text = sequence.name
            
            children = ET.SubElement(project, 'children')
            seq = ET.SubElement(children, 'sequence')
            seq_name = ET.SubElement(seq, 'name')
            seq_name.text = sequence.name
            
            rate = ET.SubElement(seq, 'rate')
            timebase = ET.SubElement(rate, 'timebase')
            timebase.text = str(int(sequence.framerate))
            
            media = ET.SubElement(seq, 'media')
            video = ET.SubElement(media, 'video')
            track = ET.SubElement(video, 'track')
            
            # Simple timeline construction mapping each clip sequentially
            current_frame = 0
            for i, c in enumerate(clips):
                clipitem = ET.SubElement(track, 'clipitem', id=f"clipitem-{i}")
                c_name = ET.SubElement(clipitem, 'name')
                c_name.text = c.asset_path.name
                
                rate_c = ET.SubElement(clipitem, 'rate')
                tb_c = ET.SubElement(rate_c, 'timebase')
                tb_c.text = str(int(sequence.framerate))
                
                file_elem = ET.SubElement(clipitem, 'file', id=f"file-{i}")
                pathurl = ET.SubElement(file_elem, 'pathurl')
                pathurl.text = f"file://localhost/{c.asset_path.as_posix()}"
                
                # Calculate frames
                start_frame = int(c.start_time * sequence.framerate)
                end_frame = int(c.end_time * sequence.framerate)
                duration_frames = end_frame - start_frame
                
                in_point = ET.SubElement(clipitem, 'in')
                in_point.text = str(start_frame)
                out_point = ET.SubElement(clipitem, 'out')
                out_point.text = str(end_frame)
                
                start = ET.SubElement(clipitem, 'start')
                start.text = str(current_frame)
                end = ET.SubElement(clipitem, 'end')
                end.text = str(current_frame + duration_frames)
                
                current_frame += duration_frames
                
            # Formatting XML
            from xml.dom import minidom
            xmlstr = minidom.parseString(ET.tostring(xmeml)).toprettyxml(indent="   ")
            
            # We save it to a context accessible path or just return it as string
            self._last_xml = xmlstr
            logger.debug("Timeline XML built successfully.")
        except Exception as e:
            raise TimelineError(f"Failed to build timeline: {e}") from e
            
    def get_last_xml(self) -> str:
        return getattr(self, '_last_xml', "")
