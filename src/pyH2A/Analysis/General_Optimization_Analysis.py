import copy
import numpy as np
from pathlib import Path
from scipy.optimize import differential_evolution
from pyH2A.Discounted_Cash_Flow import Discounted_Cash_Flow
from pyH2A.Utilities.input_modification import convert_input_to_dictionary,parse_parameter, parse_parameter_to_array, get_by_path, set_by_path


def print_notification(message):
    print(f"[Notification] {message}")


def select_non_reference_value(reference, values):
	'''Select value from values which is not the reference one.
	'''

	idx = np.invert(np.equal(values, reference))
	return values[idx][0]


class General_Optimization_Analysis:
    """
    Global optimization module for pyH2A.
    Minimizes the Levelized Cost of Hydrogen (LCOH)
    by varying specified parameters within defined bounds.
    """

    def __init__(self, input_file):
        self.inp = convert_input_to_dictionary(input_file)
        print_notification("Starting General Optimization")
        self.iteration = 0

        if "Parameters - General_Optimization_Analysis" not in self.inp:
            raise KeyError("No 'Parameters - General_Optimization_Analysis' section found in input file.")

        self.pop_size = int(self.inp['General_Optimization_Analysis'].get("Population Size", {"Value": 15})["Value"])
        self.n_iter = int(self.inp['General_Optimization_Analysis'].get("Max Iterations", {"Value": 50})["Value"])
        self.samples = self.pop_size*self.n_iter
        print('SAMPLE', self.samples)
        self.h_cost = np.zeros((self.samples, 1))
        self.process_parameters()
        self.run_optimization()
        self.results = np.hstack((self.values, self.h_cost))
        self.save_results(self.inp['General_Optimization_Analysis']['Output File']['Value'])

    def process_parameters(self):
        '''
        General Optimization parameters are read from 'Parameters - General_Optimization'
        in `self.inp` and processed.
        '''

        optimizer_param = self.inp['Parameters - General_Optimization_Analysis']

        number_parameters = len(optimizer_param)

        values = np.empty((self.samples, number_parameters))
        parameters = dict()

        for counter, key in enumerate(optimizer_param):
            values_range = parse_parameter_to_array(optimizer_param[key]['Values'], delimiter=';',
                                                    dictionary=self.inp,
                                                    top_key='Parameters - General_Optimization_Analysis',
                                                    middle_key=key, bottom_key='Values',
                                                    special_values=['Base', 'Reference'],
                                                    path=key)

            values_range = values_range[np.argsort(values_range)]
            values[:, counter] = np.random.uniform(values_range[0],
                                                   values_range[1],
                                                   self.samples)

            path = parse_parameter(key)
            reference = get_by_path(self.inp, path)
            limit = select_non_reference_value(reference, values_range)

            parameters[optimizer_param[key]['Name']] = {'Parameter': path, 'Type': optimizer_param[key]['Type'],
                                              'Values': values_range, 'Reference': reference,
                                              'Index': counter, 'Input Index': counter,
                                              'Limit': limit}

        self.values = values
        self.parameters = parameters


    def save_results(self, file_name):
        '''Results of Monte Carlo simulation are saved in `file_name` and a
        formatted header is added. Contains name, parameter path, type and values range
        from `self.parameters`.
        '''

        header_string = ''
        path_string = ''
        type_string = ''
        values_string = ''

        for key in self.parameters:
            header_string += str(key) + '	'
            path_string += str(self.parameters[key]['Parameter']) + '	'
            type_string += str(self.parameters[key]['Type']) + '	'
            values_string += str(self.parameters[key]['Values']) + '	'

        header_string += 'H2 Cost'
        complete_string = header_string + '\n' + path_string + '\n' + type_string + '\n' + values_string

        np.savetxt(Path(file_name), self.results, header=complete_string, delimiter='	')

    def objective_function(self, param_values):
        """
        Objective function that logs every evaluation
        """
        input_dict = copy.deepcopy(self.inp)

        for i, (key, parameter) in enumerate(self.parameters.items()):
            self.values[self.iteration, i] = param_values[i]
            set_by_path(input_dict, parameter['Parameter'],
                        param_values[i],
                        value_type=parameter['Type'])

        dcf = Discounted_Cash_Flow(input_dict, print_info=False)
        h2_cost = dcf.h2_cost
        self.h_cost[self.iteration, 0] = h2_cost
        self.iteration += 1
        return h2_cost

    def run_optimization(self):
        """
        Run optimization and return result
        """
        bounds = [(param['Values'][0], param['Values'][1])
                  for param in self.parameters.values()]

        result = differential_evolution(
            self.objective_function,
            bounds=bounds,
            strategy='best1bin',
            maxiter=self.n_iter,
            popsize=self.pop_size,
            workers=1,
            seed=42,
            disp=True,
            polish=True
        )
        print_notification("Optimization complete!")
        for name, value in zip(self.parameters.keys(), result.x):
            print(f"Optimized {name}: {value:.3f}")
        print(f"Minimum LCOH: {result.fun:.4f} USD/kg")
