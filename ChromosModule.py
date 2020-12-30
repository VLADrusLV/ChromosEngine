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

        # Получаем данные о режиме детектирования
        data = list(map(lambda x: x.split('=')[1], self.content.get_block(mode='data')))
        zero_time = float(data[0])
        delta_time_reading = float(data[1])
        len_reading = int(data[2])
        # Преобразование времени в секунды
        self.time = np.array((range(len_reading) * delta_time_reading) - zero_time) 

        info_block = self.content.get_block(mode='passport')
        
        if database != 'None':

            self.fid_db = pd.read_excel(database)
            self.fid_db.index = self.fid_db['Comp']

        for info in info_block:
            
            if info.find('Filename') == 0:
                
                self.full_way = info
                self.file_name = info.split('\\')[-1]
                
            if info.find('AnalyseTime') == 0:
                
                self.process = info[12:]

        # self.correct_df = pd.DataFrame(columns=['Time', 'Area', 'Comp'])

    def correct_time(self):

        

    # Функция корректирует результаты площади с учетом поправ коэф в любом виде
    def correct_area(self, mode='fid_conc'):
        
        self.correct_df['Area'] = self.df['Area'] * self.fid_db['K_g']
        self.correct_df['K_g'] = self.fid_db['K_g']
        
        if mode == 'fid_conc':

            self.correct_df['Mass_Conc'] = self.correct_df['Area'] / self.correct_df['Area'].sum()

        if mode == 'mol_conc':
            
            self.correct_df['Mass_Conc'] = self.correct_df['Area'] / self.correct_df['Area'].sum()
            self.correct_df['Mol_Area'] = self.correct_df['Area'] / self.fid_db['Mass']
            self.correct_df['Mol_Conc'] = self.correct_df['Mol_Area'] / self.correct_df['Mol_Area'].sum()
            self.correct_df = self.correct_df.drop(columns=['Mol_Area'])

    def sum_area_no_id_fid(self):

        # Запоминаем максимальные значения времени удерживаня
        max_time = self.df['Time'].max()
        # Базовые параметры для анализа хроматограмм
        basic_parameters = ['Time','Area']
        # Групируем все компоненты NO_ID сумируются
        self.correct_df = self.df.groupby(['Comp'])[basic_parameters].mean()
        # Добовляем к комп NO_ID максимальное время, что бы точно был в конце
        
        try:
            self.correct_df.loc['No_ID']['Time'] = max_time + 1
        except KeyError:
            pass
            
           
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

if __name__ == "__main__":
    pass

else:
    print('ChromosArray was conected')