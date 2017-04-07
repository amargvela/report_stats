import sys
import process_results
import numpy as np

def main(train_file, dev_file, test_file):
        #train_results = process_results.get_results(train_file)
        dev_results = process_results.get_results(dev_file)
        test_results = process_results.get_results(test_file)

#        false_negative_threshold = 0.001
        false_negative_threshold = 0.001*90
        best_true_negative_rate = -1
        true_negative_rates = []
        best_result_index = -1
        best_per_epoch = {}
        epoch = 0
        num_patients = 0
        best_epoch = 0

        for k in range(len(dev_results)):
                result = dev_results[k]
                test_result = result['dev']
                false_positive_rate = test_result['fpr2']
                true_positive_rate = test_result['tpr2']
                print(true_positive_rate)
                for i in range(len(false_positive_rate)):
                        false_negative_rate = (1.0 - true_positive_rate[i])
                        if false_negative_rate < false_negative_threshold:
                                true_negative_rate = 1 - false_positive_rate[i]
                                true_negative_rates.append(true_negative_rate)
                                threshold = test_result['thresholds2'][i]
                                new_index = translate_from_threshold_to_index(test_result, threshold)
                                print('transfer', i, new_index)
                                true_negative_rate_true = 1 - test_result['fpr'][new_index]

                                if true_negative_rate_true > best_true_negative_rate and threshold > 0 and threshold < 1:
                                        best_true_negative_rate = true_negative_rate_true
                                        # print('best', best_true_negative_rate)
                                        best_result_index = k
                                        best_threshold = threshold
                                        best_per_epoch[epoch] = threshold
                                        best_epoch = epoch
                                        break
                epoch += 1

        best_dev_result = dev_results[best_result_index]
        best_test_result = test_results[best_result_index]
        negative_ratio_in_data = 0.96
        positive_ratio_in_data = 1 - negative_ratio_in_data
        print('best_true_negative', best_true_negative_rate)
        print('best_threshold', best_threshold)
        best_dev_index = translate_from_threshold_to_index(best_dev_result['dev'], best_threshold)
        # print(best_dev_index, len(results[0]['dev']['fpr']), len(best_result['dev']['fpr']))
        best_test_index = translate_from_threshold_to_index(best_test_result['test'], best_threshold)

        dev_best = 1 - best_dev_result['dev']['fpr'][best_dev_index]
        best_dev_ratio = dev_best * negative_ratio_in_data + false_negative_threshold * positive_ratio_in_data
        average_negative_ratio_by_model = 1.0 * np.array(true_negative_rates) * negative_ratio_in_data + false_negative_threshold * positive_ratio_in_data
        average_negative_ratio_by_model = np.sum(average_negative_ratio_by_model) / len(average_negative_ratio_by_model)

        num_epochs = dev_results[-1]['epoch'] + 1

        test_best = 1 - best_test_result['test']['fpr'][best_test_index]
        best_test_ratio = test_best * negative_ratio_in_data + false_negative_threshold * positive_ratio_in_data
        # best_i = float(best_per_epoch[0])/len(results[0]['dev']['fpr'])
        # print(best_i)
        best_random_test_index = translate_from_threshold_to_index(test_results[0]['test'], best_per_epoch[0])
        best_random_dev_index = translate_from_threshold_to_index(dev_results[0]['dev'], best_per_epoch[0])
        test_random = 1 - test_results[0]['test']['fpr'][best_random_test_index]
        best_random_test = test_random * negative_ratio_in_data + false_negative_threshold * positive_ratio_in_data

        dev_random = 1 - dev_results[0]['dev']['fpr'][best_random_dev_index]
        best_random_dev = dev_random * negative_ratio_in_data + false_negative_threshold * positive_ratio_in_data

        print 'Best % triage dev {:.2f}% for false_negative_threshold {:.1f}% on epoch {:d} out of {:d} epochs'.format(100*best_dev_ratio, 100*false_negative_threshold, best_dev_result['epoch'], num_epochs)
        print 'Best % triage test {:.2f}% for false_negative_threshold {:.1f}% on epoch {:d} out of {:d} epochs'.format(100*best_test_ratio, 100*false_negative_threshold, best_dev_result['epoch'], num_epochs)

        print 'Best % triage random dev {:.2f}% for false_negative_threshold {:.1f}% on epoch {:d} out of {:d} epochs'.format(100*best_random_dev, 100*false_negative_threshold, 0, num_epochs)
        print 'Best % triage random test {:.2f}% for false_negative_threshold {:.1f}% on epoch {:d} out of {:d} epochs'.format(100*best_random_test, 100*false_negative_threshold, 0, num_epochs)

        print 'Average negative_ratio_by_model {:.2f}% for {:d} epochs'.format(100*average_negative_ratio_by_model, num_epochs)
        print 'Test accuracy for best negative_ratio_by_model {:.2f}%'.format(100*best_test_result['test']['accuracy'])
        print 'confusion matrix for best negative_ratio_by_model'
        print np.array(best_test_result['test']['confusion_matrix'])



def translate_from_threshold_to_index(result, target_threshold, key='thresholds'):
        closest_threshold_index = -1
        best_threshold_distance = 100
        for i in range(len(result[key])):
                result_threshold = result[key][i]
                # print('targ, result', target_threshold, result_threshold)
                result_threshold_distance = (result_threshold - target_threshold)**2.0
                if result_threshold_distance < best_threshold_distance and target_threshold > result_threshold:
                        closest_threshold_index = i
                        best_threshold_distance = result_threshold_distance
        return closest_threshold_index


if __name__ == '__main__':
    _, train_file, dev_file, test_file = sys.argv
    main(train_file, dev_file, test_file)

