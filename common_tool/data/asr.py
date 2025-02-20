from collections import defaultdict
from abc import ABCMeta


class Time:
    def __init__(self, start, end):
        self.begin = start
        self.end = end


class Sentence:
    def __init__(self, speaker, seg_id):
        self.time = Time(0, 0)
        self.text = ""
        self.speaker = speaker
        self.xf_seg_id = seg_id

    def time_begin(self, begin):
        self.time.begin = begin

    def time_end(self, end):
        self.time.end = end

    def add_text(self, word: str):
        self.text = f"{self.text}{word}"

    def __str__(self):
        return f"{self.time.begin}-{self.time.end} {self.speaker}: {self.text}"


class Content:
    def __init__(self):
        self._c: [Sentence] = []
        self._speaker_c = defaultdict(list)
        self._time_c = defaultdict(list)

    def add(self, s: Sentence):
        self._c.append(s)
        self._speaker_c[s.speaker].append(s)
        self._time_c[s.time].append(s)

    def add_punc(self, punc: str, speaker: str) -> bool:
        """
        标点符号在话语结束后的下一句一起返回
        """
        if len(self._c) == 0:
            return False
        if self._c[-1].speaker != speaker:
            return False
        self._c[-1].text += punc
        return True

    def __str__(self):
        return "\n".join([str(item) for item in self._c])


class VoiceAsrData(metaclass=ABCMeta):
    def __init__(self, asr_data: dict):
        self._asr_data = asr_data

    def parse(self):
        pass

    def sentences(self):
        pass
