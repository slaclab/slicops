/**
 * Numeric (integer or float) field validation.
 */
import { watch } from 'vue'
import { useValidation } from '@/components/widget/validation/useValidation.js'

export function useNumberValidation(field) {
    const NUMBER_REGEXP = /^\s*(\-|\+)?(\d+|(\d*(\.\d*)))([eE][+-]?\d+)?\s*$/;
    const { isInvalid, parsedValue, rawValue } = useValidation(field);
    const isNumber = (value) => typeof value === 'number';

    watch(rawValue, () => {
        if (isInvalid.value) {
            return;
        }
        if (field.optional && rawValue.value === '') {
            return;
        }
        if (! NUMBER_REGEXP.test(rawValue.value)) {
            isInvalid.value = true;
            return;
        }
        parsedValue.value = parseFloat(rawValue.value);
        if (field.widget === 'integer') {
            parsedValue.value = parseInt(parsedValue.value);
        }
        if (field.constraints) {
            if (isNumber(field.constraints.min)) {
                if (parsedValue.value < field.constraints.min) {
                    isInvalid.value = true;
                    return;
                }
            }
            if (isNumber(field.constraints.max)) {
                if (parsedValue.value > field.constraints.max) {
                    isInvalid.value = true;
                    return;
                }
            }
        }
    });

    return { isInvalid, parsedValue, rawValue };
}
