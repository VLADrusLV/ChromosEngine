# Есть основное ядро движка которая обрабатывает данные из файлов
from ChromosEngine.ChromosCore import ChromosData 


# Все работает на основных и базовых библиотеках
import numpy as np
import pandas as pd

# Здесь просто наследуем основной функционал
class ChromosArray(ChromosData):
    
    """
    Класс для работы с хроматограммами как с массивами
    """
    
    def __init__(self, file, database=None):
        
        # Данные храниться в текстовом файле поэтому с ним и работаем
        self.content = ChromosData(file)
        
        # Получаем полный массив хроматограммы
        self.samples = np.array(self.content.get_block(mode='samples'), float)
        
        # Удобнее работать и хранить всю инфу по пикам в виде датафрейма
        self.df = self.content.get_peaks(mode='dataframe')

        # Получаем данные о режиме детектирования
        data = list(map(lambda x: x.split('=')[1], self.content.get_block(mode='data')))
        zero_time = float(data[0])
        delta_time_reading = float(data[1])
        len_reading = int(data[2])
        # Преобразование времени в сeекунд
        self.time = (np.array(range(len_reading)) * delta_time_reading) - zero_time

        info_block = self.content.get_block(mode='passport')
        
        if database:

            self.fid_db = pd.read_excel(database)
            self.fid_db.index = self.fid_db['Comp']
            self.len_db = len(self.fid_db)
            self.fid_db = self.fid_db.sort_values(by=['RT'])
            print(f'Database FID was conecting - {database}')

        for info in info_block:
            
            if info.find('Filename') == 0:
                
                self.full_way = info
                self.file_name = info.split('\\')[-1]
                
            if info.find('AnalyseTime') == 0:
                
                self.process = info[12:]

        # self.correct_df = pd.DataFrame(columns=['Time', 'Area', 'Comp'])

    def find_component_in_db(self, time_test_comp, right_time=0.3):

        min_delta = None
        find_index = None
        comp = 'No_ID'

        for db_index in range(self.len_db):
                    
            test_delta_time = abs(time_test_comp - self.fid_db.iloc[db_index]['RT'])
            
            if db_index == 0:

                min_delta = test_delta_time

            if test_delta_time <= min_delta and test_delta_time <= right_time:
                
                min_delta = test_delta_time
                find_index = db_index

        if find_index is not None:

            comp = self.fid_db.iloc[find_index]['Comp']
        
        return comp, min_delta
    
    def correct_time(self, mode='height', time_around=0.5):

        if mode == 'height':
            
            self.correct_df = self.df.copy()
            temp_df_for_ind = self.df.sort_values(by=['Height'], ascending=False)
            first_comp, first_delta_time = self.find_component_in_db(temp_df_for_ind.iloc[0]['Time'], right_time=time_around)
            self.correct_df['Time'] = self.correct_df['Time'] + first_delta_time
            height_first_comp = temp_df_for_ind.iloc[0]['Height']
            height_second_comp = temp_df_for_ind.iloc[1]['Height']
            min_height_comp = temp_df_for_ind.iloc[-1]['Height']
            
            print('Time was correcting by Height')
            print(f'Component with very height intensity is {first_comp}')
            print(f'Intensity of very height component is {height_first_comp}')
            print(f'Min intensity of component chromatography is {min_height_comp}')
            print(first_delta_time)

            second_comp, second_delta_time = self.find_component_in_db(temp_df_for_ind.iloc[1]['Time'], right_time=time_around)
            
            print(f'Component with second height intensity is {second_comp}')
            print(f'Height of second comp is {height_second_comp}')
            print(second_delta_time)
            print(f'Error is {second_delta_time - first_delta_time}')

        if mode == 'first':

            self.correct_df = self.df.copy()
            comp, delta_time = self.find_component_in_db(self.df.iloc[0]['Time'], right_time=time_around)
            self.correct_df['Time'] = self.correct_df['Time'] + delta_time
            print('Time was correcting by first peak')
            print(comp)
            print(delta_time)

        return first_delta_time

    def detection_comp(self):

        comp_list = []
        error_list = []

        for index in range(len(self.correct_df)):
            
            time = self.correct_df.iloc[index]['Time']

            comp, delta_time = self.find_component_in_db(time, right_time=0.15)
            
            comp_list.append(comp)
            error_list.append(delta_time)

        self.correct_df['Comp'] = comp_list
        self.correct_df['Error'] = error_list
        

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
        max_time = self.correct_df['Time'].max()
        # Базовые параметры для анализа хроматограмм
        basic_parameters = ['Time','Area']
        # Групируем все компоненты NO_ID сумируются
        self.correct_df = self.correct_df.groupby(['Comp'])[basic_parameters].mean()
        # Добовляем к комп NO_ID максимальное время, что бы точно был в конце
        
        try:
            self.correct_df.loc['No_ID']['Time'] = max_time + 1
        except KeyError:
            pass

        self.correct_df = self.correct_df.sort_values(by=['Time'])

            
           
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

        self.x = self.x + delta_time

    def shift_height(self, delta_height):

        self.y = self.y + delta_height

if __name__ == "__main__":
    
    pass

else:
    print('ChromosArray was conected')
