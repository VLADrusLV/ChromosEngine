import pandas as pd
from collections import namedtuple
import numpy as np

class ChromosData():

    def __init__(self, chromos_export_file):
        
        with open(chromos_export_file, 'r', encoding='cp1251') as chromos_file:
            # Cчитываем построчно файл и записываем в список
            unformat_data = chromos_file.read().split('\n')
            # Чистим от пустых строк
            self.data = list(filter(lambda x: False if x == '' else x.strip(), unformat_data))

    # Получаем данные для работы в виде листа
    def get_block(self, mode='peaks'):

        list_separations = ['passport', 'peaks', 'groups', 'data', 'samples']

        Block = namedtuple('Block', list_separations)
        
        blocks = Block('[Passport]', '[Peaks]', '[Groups]', '[Data]', '[Samples]')
        
        # Узнаем индекс для входных данных 1 для перехода на следующую строку
        current_index = list_separations.index(mode)

        open_index = self.data.index(blocks[current_index]) + 1

        current_index += 1

        try:                                   
            # Находим закрывающий индекс Groups
            close_index = self.data.index(blocks[current_index])
    
        # Если идентификатора блока переходим на следующий
        except ValueError:

            current_index += 1
            # Находим закрывающий индекс Groups
            close_index = self.data.index(blocks[current_index])
            return self.data[open_index : close_index]

        # Значит в конце списка считываем до конца
        except IndexError:

            return self.data[open_index :]

        # В конце получаем результат
        else:

            return self.data[open_index : close_index]

            

    # Метод для перевода данных в пике в нужный формат
    def get_peaks(self, mode='dict'):

        # Получаем лист с данными 
        data = self.get_block(mode='peaks')

        # Создаём списки где будем хранить Номер, Время, Высота, Площадь, Концентрацию и Идентификации пика
        Number = []
        Time = []
        Height = []
        Surface = []
        Conc = []
        Id = []
            
        # Создаём временный список для считывания строки
        temp_list = []

        # Цикл для заполнения данных в соответствующие списки
        for line in data:
                
            # Считываем временный список и разделяем по запятым
            temp_list = line.split(',')

            # Вносим номер пика в список и чистим от пробелов
            temp_number = temp_list[0]

            Number.append(int(temp_number.strip()))
                    
            # Вносим время удерживания пика в список и чистим от пробелов
            temp_time = temp_list[1]

            Time.append(float(temp_time.strip()))

            # Вносим высоту пика в список и чистим от пробелов
            temp_height = temp_list[2]

            Height.append(float(temp_height.strip()))

            # Вносим площадь пика в список и чистим от пробелов
            temp_surface = temp_list[3]

            Surface.append(float(temp_surface.strip()))
                    
            # Вносим концентрацию компонента пика в список и чистим от пробелов
            temp_conc = temp_list[4]

            Conc.append(float(temp_conc.strip()))

            # Вносим название нужного компонента, при этом обьеденяем ячейки с назвннием
            # Так как они крайние

            temp_id = temp_list[5:]
            temp_id = ', '.join(temp_id)

            # Если компонент неизвестен записываем No_ID
            if temp_id == ' "-"':
                Id.append('No_ID')
                    
            # Если известен вносим название компонента и убираем кавычки 1,2 и последний символ
            else:
                Id.append(temp_id[2:-1])

            # Чистим временный список
            temp_list.clear()

        result_dict = {
                'Time' : Time, 
                'Area' : Surface,
                'Height': Height, 
                'Conc' : Conc, 
                'Comp' : Id
                }

        if mode == 'dict':

            # Создаём словарь для Data Frame (библ. Pandas)
            return result_dict
        
        elif mode == 'dataframe':

            df = pd.DataFrame(result_dict)
            df.index.name = 'Num'
            return df





if __name__ == "__main__":
    
    pass
    
else:
    print('ChromosCore was conected')







