<template>
    <!-- Main modal -->
    <div
        class="fixed inset-0 z-50 flex h-screen w-screen justify-center bg-slate-600 bg-opacity-10 pt-24 backdrop-blur-[1.5px]"
        @click.self="emits('hide')"
        v-if="props.show"
    >
        <div
            id="default-modal"
            tabindex="-1"
            aria-hidden="true"
            class="z-50 overflow-y-auto overflow-x-hidden"
        >
            <div class="relative max-h-full w-full max-w-2xl p-4">
                <!-- Modal content -->
                <div
                    class="relative min-w-96 rounded-lg bg-white shadow dark:bg-gray-700"
                >
                    <!-- Modal header -->
                    <div
                        class="flex items-center justify-between rounded-t border-b p-4 md:p-5 dark:border-gray-600"
                    >
                        <h3
                            class="text-xl font-semibold text-gray-900 dark:text-white"
                        >
                            {{ props.title }}
                        </h3>
                        <button
                            type="button"
                            class="ms-auto inline-flex h-8 w-8 items-center justify-center rounded-lg bg-transparent text-sm text-gray-400 hover:bg-gray-200 hover:text-gray-900 dark:hover:bg-gray-600 dark:hover:text-white"
                            @click="emits('hide')"
                        >
                            <svg
                                class="h-3 w-3"
                                aria-hidden="true"
                                xmlns="http://www.w3.org/2000/svg"
                                fill="none"
                                viewBox="0 0 14 14"
                            >
                                <path
                                    stroke="currentColor"
                                    stroke-linecap="round"
                                    stroke-linejoin="round"
                                    stroke-width="2"
                                    d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6"
                                />
                            </svg>
                            <span class="sr-only">Close modal</span>
                        </button>
                    </div>
                    <!-- Modal body -->
                    <div class="space-y-4 p-4 md:p-5">
                        <slot></slot>
                    </div>
                    <!-- Modal footer -->
                    <div
                        v-if="props.acceptButton || props.declineButton"
                        class="flex items-center rounded-b border-t border-gray-200 p-4 md:p-5 dark:border-gray-600"
                    >
                        <slot name="buttons">
                            <button
                                v-if="props.acceptButton"
                                @click="emits('accept')"
                                type="button"
                                class="rounded-lg bg-blue-700 px-5 py-2.5 text-center text-sm font-medium text-white hover:bg-blue-800 focus:outline-none focus:ring-4 focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
                            >
                                {{ props.acceptButton }}
                            </button>
                            <button
                                v-if="props.declineButton"
                                @click="emits('decline')"
                                type="button"
                                class="ms-3 rounded-lg border border-gray-200 bg-white px-5 py-2.5 text-sm font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-900 focus:z-10 focus:outline-none focus:ring-4 focus:ring-blue-300 dark:border-gray-500 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 dark:hover:text-white dark:focus:ring-gray-600"
                            >
                                {{ props.declineButton }}
                            </button>
                        </slot>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
const props = withDefaults(
    defineProps<{
        title?: string;
        acceptButton?: string;
        declineButton?: string;
        show?: boolean;
    }>(),
    {
        show: false,
    },
);

// const hide = () => props.show = false
const emits = defineEmits<{
    (e: "hide"): void;
    (e: "accept"): void;
    (e: "decline"): void;
}>();
</script>
