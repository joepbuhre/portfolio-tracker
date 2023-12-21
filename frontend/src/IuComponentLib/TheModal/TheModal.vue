<template>
    <!-- Main modal -->
    <div
        class="flex justify-center pt-24 fixed z-50 w-screen h-screen inset-0 bg-slate-600 bg-opacity-10 backdrop-blur-[1.5px]"
        @click.self="emits('hide')"
        v-if="props.show"
    >
        <div
            id="default-modal"
            tabindex="-1"
            aria-hidden="true"
            class="overflow-y-auto overflow-x-hidden z-50"
        >
            <div class="relative p-4 w-full max-w-2xl max-h-full">
                <!-- Modal content -->
                <div
                    class="relative bg-white rounded-lg shadow dark:bg-gray-700 min-w-96"
                >
                    <!-- Modal header -->
                    <div
                        class="flex items-center justify-between p-4 md:p-5 border-b rounded-t dark:border-gray-600"
                    >
                        <h3
                            class="text-xl font-semibold text-gray-900 dark:text-white"
                        >
                            {{ props.title }}
                        </h3>
                        <button
                            type="button"
                            class="text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm w-8 h-8 ms-auto inline-flex justify-center items-center dark:hover:bg-gray-600 dark:hover:text-white"
                            @click="emits('hide')"
                        >
                            <svg
                                class="w-3 h-3"
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
                    <div class="p-4 md:p-5 space-y-4">
                        <slot></slot>
                    </div>
                    <!-- Modal footer -->
                    <div
                        v-if="props.acceptButton || props.declineButton"
                        class="flex items-center p-4 md:p-5 border-t border-gray-200 rounded-b dark:border-gray-600"
                    >
                        <button
                            v-if="props.acceptButton"
                            @click="emits('hide')"
                            type="button"
                            class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800"
                        >
                            {{ props.acceptButton }}
                        </button>
                        <button
                            v-if="props.declineButton"
                            @click="emits('hide')"
                            type="button"
                            class="ms-3 text-gray-500 bg-white hover:bg-gray-100 focus:ring-4 focus:outline-none focus:ring-blue-300 rounded-lg border border-gray-200 text-sm font-medium px-5 py-2.5 hover:text-gray-900 focus:z-10 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-500 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-600"
                        >
                            {{ props.declineButton }}
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">

const props = withDefaults(defineProps<{
    title?: string,
    acceptButton?: string,
    declineButton?: string,
    show?: boolean
}>(), {
    show: false
})

// const hide = () => props.show = false
const emits = defineEmits<{
    (e: "hide"): void;
}>()



</script>
