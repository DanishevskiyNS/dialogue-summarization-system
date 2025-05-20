class DialogueParserModule:
    @staticmethod
    def format_as_dialogue(transcription_segments, diarization_segments) -> str:
        """Форматирует сегменты транскрипции и диаризации в диалог.
        
        Args:
            transcription_segments: Список сегментов транскрипции с временными метками
            diarization_segments: Список сегментов диаризации с ID говорящих
            
        Returns:
            str: Отформатированный диалог
        """
        dialogue_lines = []
        current_speaker = None
        
        # Сортируем сегменты по времени начала
        transcription_segments = sorted(transcription_segments, key=lambda x: x["start"])
        diarization_segments = sorted(diarization_segments, key=lambda x: x["start"])
        
        di = 0  # индекс текущего сегмента диаризации
        
        for trans in transcription_segments:
            trans_start = trans["start"]
            trans_end = trans["end"]
            
            # Ищем соответствующий сегмент диаризации
            while di < len(diarization_segments):
                diar = diarization_segments[di]
                
                # Если сегмент диаризации после текущей транскрипции
                if diar["start"] >= trans_end:
                    # Используем последнего известного говорящего
                    if current_speaker:
                        dialogue_lines.append(f"#{current_speaker}#: {trans['transcription']}")
                    break
                
                # Если есть перекрытие между сегментами
                if (diar["start"] <= trans_end and diar["end"] >= trans_start):
                    current_speaker = diar["speaker_id"]
                    dialogue_lines.append(f"#{current_speaker}#: {trans['transcription']}")
                    break
                
                di += 1
                
            # Если достигли конца диаризации, используем последнего говорящего
            if di >= len(diarization_segments) and current_speaker:
                dialogue_lines.append(f"#{current_speaker}#: {trans['transcription']}")
        
        return "\n".join(dialogue_lines)