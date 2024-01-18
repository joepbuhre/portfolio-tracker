<template>
    <div class="flex w-full items-center justify-center">
        <label
            for="dropzone-file"
            class="dark:hover:bg-bray-800 flex h-64 w-full cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 hover:bg-gray-100 dark:border-gray-600 dark:bg-gray-700 dark:hover:border-gray-500 dark:hover:bg-gray-600"
        >
            <div
                v-if="file === null"
                class="flex flex-col items-center justify-center pb-6 pt-5"
            >
                <svg
                    class="mb-4 h-8 w-8 text-gray-500 dark:text-gray-400"
                    aria-hidden="true"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 20 16"
                >
                    <path
                        stroke="currentColor"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M13 13h3a3 3 0 0 0 0-6h-.025A5.56 5.56 0 0 0 16 6.5 5.5 5.5 0 0 0 5.207 5.021C5.137 5.017 5.071 5 5 5a4 4 0 0 0 0 8h2.167M10 15V6m0 0L8 8m2-2 2 2"
                    />
                </svg>
                <p class="mb-2 text-sm text-gray-500 dark:text-gray-400">
                    <span class="font-semibold">Click to upload</span> or drag
                    and drop
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                    Accounts.csv
                </p>
            </div>
            <div v-else class="m-auto text-center">
                <div>{{ file?.name }}</div>
                <button
                    class="button today-btn !bg-primary-700 dark:!bg-primary-600 hover:!bg-primary-800 dark:hover:!bg-primary-700 focus:!ring-primary-300 mt-2 rounded-lg bg-blue-700 px-3 py-1 text-center text-sm font-medium text-white hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700"
                    @click="emits('upload', file)"
                >
                    Upload
                </button>
            </div>
            <!-- <span >
                {{ file.name }}
                {{ file.type }}
                {{ DateFormatter.format(new Date(file.lastModified)) }}
            </span> -->

            <input
                id="dropzone-file"
                type="file"
                class="hidden"
                @change="handleFile"
            />
        </label>
    </div>
</template>

<script setup lang="ts">
import { DateFormatter } from "@src/utils/formatters";
import { ref } from "vue";

const emits = defineEmits<{
    (e: "upload", value: File): void;
}>();

const file = ref<null | File>(null);

const handleFile = (e: Event) => {
    const target = e.target as HTMLInputElement;

    if (target?.files?.length && target?.files?.length > 0) {
        file.value = target.files[0];
    }

    // if (file.value !== null) {
    //     emits("upload", file.value);
    // }
};
</script>
