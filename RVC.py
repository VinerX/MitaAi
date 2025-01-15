import torch
import librosa
import soundfile as sf


class BnmRvcModel:
    def __init__(self, model_path="RVC/experiment_mita.pth",index_path="RVC/added_IVF392_Flat_nprobe_1_experiment_mita_v2.index", device=None):
        """
        Инициализация модели BNM RVC.

        :param model_path: Путь к файлу модели (.pth).
        :param device: Устройство для выполнения ("cuda" или "cpu"). Если None, выбирается автоматически.
        """
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_model(model_path)
        self.index = self._load_index(index_path) if index_path else None
    def _load_model(self, model_path):
        """
        Загружает модель на заданное устройство.

        :param model_path: Путь к файлу модели.
        :return: Загруженная модель.
        """
        model = torch.load(model_path, map_location=torch.device(self.device))
        model.eval()
        return model
    def _load_index(self, index_path):
        """Загружает файл индекса."""
        # Здесь можно реализовать загрузку индекса (например, JSON, YAML или другой формат).
        with open(index_path, "r") as f:
            index_data = f.read()
        # Предполагается, что в файле индекса структура данных, которую использует ваша модель.
        return index_data
    def preprocess_audio(self, input_wav, target_sr=16000):
        """
        Предобработка аудио: загрузка и приведение к нужной частоте дискретизации.

        :param input_wav: Путь к входному аудио.
        :param target_sr: Частота дискретизации (по умолчанию 16000 Гц).
        :return: Тензор с аудио данными.
        """
        audio, sr = librosa.load(input_wav, sr=target_sr, mono=True)
        return torch.tensor(audio, dtype=torch.float32).unsqueeze(0).to(self.device)

    def apply_model(self, input_audio):
        """
        Применяет модель к входным данным.

        :param input_audio: Тензор с аудио данными.
        :return: Преобразованный аудиосигнал в формате numpy.
        """
        with torch.no_grad():
            if self.index:
                # Пример: если модель ожидает индекс как отдельный аргумент
                transformed_audio = self.model(input_audio, index=self.index)
            else:
                transformed_audio = self.model(input_audio)
        return transformed_audio.squeeze(0).cpu().numpy()

    def save_audio(self, output_path, audio, sr=16000):
        """
        Сохраняет аудио в файл.

        :param output_path: Путь для сохранения.
        :param audio: Аудио данные в формате numpy.
        :param sr: Частота дискретизации.
        """
        sf.write(output_path, audio, sr)

    def process(self, input_wav, output_wav, target_sr=16000):
        """
        Полный процесс преобразования: загрузка, обработка, сохранение.

        :param input_wav: Путь к входному аудио файлу.
        :param output_wav: Путь для сохранения результата.
        :param target_sr: Частота дискретизации (по умолчанию 16000 Гц).
        """
        input_audio = self.preprocess_audio(input_wav, target_sr)
        transformed_audio = self.apply_model(input_audio)
        self.save_audio(output_wav, transformed_audio, sr=target_sr)

"""
# Пример использования
if __name__ == "__main__":
    model_path = "path_to_your_model.pth"
    input_wav = "input.wav"
    output_wav = "output.wav"

    bnm_rvc = BnmRvcModel(model_path)
    bnm_rvc.process(input_wav, output_wav)
"""