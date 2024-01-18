<template>
    <div
        id="toast-default"
        class="flex w-full max-w-xs items-center rounded-lg border border-gray-300 bg-white p-4 text-gray-500 shadow-lg dark:bg-gray-800 dark:text-gray-400"
        :class="{
            'shadow-blue-100': props.type === ToastType.Success,
            'shadow-red-100': props.type === ToastType.Error,
        }"
        role="alert"
    >
        <div
            class="inline-flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg"
            :class="{
                'bg-blue-100 text-blue-500 dark:bg-blue-800 dark:text-blue-200':
                    props.type === ToastType.Success,
                'bg-red-100 text-red-500 dark:bg-red-800 dark:text-red-200':
                    props.type === ToastType.Error,
            }"
        >
            <slot name="icon">
                <AlertTriangleIcon :size="20" v-if="ToastType.Error" />
                <InfoIcon :size="20" v-else />
            </slot>
            <span class="sr-only">Fire icon</span>
        </div>
        <div class="ms-3 px-4 text-sm font-normal">
            <slot></slot>
        </div>
        <button
            type="button"
            class="-mx-1.5 -my-1.5 ms-auto inline-flex h-8 w-8 items-center justify-center rounded-lg bg-white p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-900 focus:ring-2 focus:ring-gray-300 dark:bg-gray-800 dark:text-gray-500 dark:hover:bg-gray-700 dark:hover:text-white"
            data-dismiss-target="#toast-default"
            aria-label="Close"
            @click="emit('close')"
        >
            <span class="sr-only">Close</span>
            <XIcon />
        </button>
    </div>
</template>
<script setup lang="ts">
import { InfoIcon } from "lucide-vue-next";
import { XIcon } from "lucide-vue-next";
import { ToastType } from "./enums";
import { AlertTriangleIcon } from "lucide-vue-next";

const props = withDefaults(
    defineProps<{
        type?: ToastType;
    }>(),
    {
        type: ToastType.Success,
    },
);

const emit = defineEmits<{
    (e: "close"): void;
}>();
</script>
