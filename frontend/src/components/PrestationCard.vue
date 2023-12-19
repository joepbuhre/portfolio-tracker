<template>
    <div class="px-5 py-2 bg-blue-50 rounded shadow-sm">
        <div class="text-base text-gray-400">{{ title }}</div>
        <div class="flex items-center pt-1">
            <div class="text-2xl font-bold text-gray-900">
                {{ currentValue }}
            </div>
            <span
                v-if="props.differenceValue"
                class="flex items-center px-2 py-0.5 mx-2 text-sm  rounded-full"
                :class="{
                    'text-green-600 bg-green-100': props.differenceValue > 0,
                    'text-red-600 bg-red-100': props.differenceValue < 0

                }"
            >
                <span>
                    <ChevronUpIcon :size="18" v-if="props.differenceValue > 0" />
                    <ChevronDownIcon :size="18" v-else />
                </span>
                <span>{{ differenceValue }}</span>
            </span>
        </div>
    </div>
</template>
<script setup lang="ts">
import { computed } from "vue";

import { ChevronUpIcon, ChevronDownIcon } from "lucide-vue-next";

export interface PrestationCardProps {
    title: string;
    currentValue: number;
    currentValueFormat?: Intl.NumberFormat;
    differenceValue?: number;
    differenceValueFormat?: Intl.NumberFormat;
}

const props = defineProps<PrestationCardProps>();

const currentValue = computed((): string =>
    props.currentValueFormat
        ? props.currentValueFormat.format(props.currentValue)
        : props.currentValue.toString()
);

const differenceValue = computed((): string =>{
    if (props.differenceValue) {
        return props.differenceValueFormat
            ? props.differenceValueFormat.format(props.differenceValue)
            : props.differenceValue.toString()
        } else {
            return ''
        }
    }
);
</script>
