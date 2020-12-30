from ChromosEngine.ChromosCore import ChromosData 

import numpy as np
import pandas as pd

class ChromosArray(ChromosData):
    
    """
    Класс для работы с хроматограммами как с массивами
    """
    
    def __init__(self, file, database=None):
        
        # Данные храниться в текстовом файле поэтому с ним и работаем
        self.content = ChromosData(file)
        
        # Получаем полный массив хроматограммы
        self.samples = np.array(self.content.get_block(mode='samples'), float)
        # Удобнее работать и хранить всю инфу в виде датафрейма
        self.df = self.content.get_peaks(mode='dataframe')

        # Получаем данные о режиме сьемки
        data = list(map(lambda x: x.split('=')[1], self.content.get_block(mode='data')))
        self.t0 = float(data[0])
        self.dt = float(data[1])
        self.len = int(data[2])
        # Преобразование времени в секунды
        self.time = np.array(range(int(data[2]))) * float(data[1])
        info_block = self.content.get_block(mode='passport')

        for info in info_block:
            
            if info.find('Filename') == 0:
                
                self.name = info
                self.file = info.split('\\')[-1]
                
            if info.find('AnalyseTime') == 0:
                
                self.process = info[12:]

            if database:

                self.fid_db = pd.read_excel(database)
                self.fid_db.index = self.fid_db['Comp']

   
    def time_slot(self, time_min, time_max):

        index_points = []
        time_filtred = []        

        # Проходимся по всему массиву времен
        for index, time in enumerate(self.time):

            # Берем нужное время
            if time >= time_min and time <= time_max:

                # Добавляем время в данном участке
                time_filtred.append(time)
                # Добавляем пик в данном участке
                index_points.append(index)                

        self.x = np.array(time_filtred)
        self.y = np.array(self.samples[index_points])
                
    
    def max_height(self, max_value):

        # Массив для хранения высот пиков
        s_arr = []
        # Определяем локальный минимум в массиве
        min_value_in_array = self.y.min()

        # Если значение меньше минимального предупрежадаем об этом и выдем ошибку
        if max_value < min_value_in_array:

            print('Your value is more then min value in array')
            return 0

        # Берем каждый из пиков из участка
        for sample in self.y:

            # Если точка больше максимально заданного
            if sample >= max_value:

                # ... Записываем заданный максимум
                s_arr.append(max_value)

            # Если точка меньше максимально заданного
            else:
                # Записываем точку как она есть
                s_arr.append(sample)

        self.y = np.array(s_arr)

    def draw(self):

        return self.x, self.y

    def reset_plot(self):

        self.x = self.time
        self.y = self.samples

    def shift_time(self, delta_time):

        self.x = self.x - delta_time

    def shift_height(self, delta_height):

        self.y = self.y + delta_height
 

