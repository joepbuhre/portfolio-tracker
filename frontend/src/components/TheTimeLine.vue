<template>
    <div class="lg:w-1/3">
        <ol class="relative border-s border-gray-200 dark:border-gray-700">
            <li v-for="(action, index) in stockActions" class="mb-10 ms-6">
                <span
                    class="absolute -start-3 flex h-6 w-6 items-center justify-center rounded-full bg-blue-100 ring-8 ring-white dark:bg-blue-900 dark:ring-gray-900"
                >
                    <!-- <img class="rounded-full shadow-lg" src="/docs/images/people/profile-picture-3.jpg" alt="Bonnie image"/> -->
                </span>
                <div
                    class="items-center justify-between rounded-lg border border-gray-200 bg-white px-4 pb-2 shadow-sm dark:border-gray-600 dark:bg-gray-700"
                >
                    <p class="mt-2 text-sm font-semibold">
                        {{ action.action }}
                        <time
                            class="text-xs font-normal text-gray-400 sm:order-last sm:mb-0"
                            >2 days ago (2023-01-01)</time
                        >
                    </p>
                    <div
                        class="mt-1 text-sm font-normal text-gray-500 dark:text-gray-300"
                    >
                        Ordered {{ action.quantity }} pc(s) for a total cost of
                        €
                        {{ -(action.transaction_cost + action.home_mutation) }}
                        <hr class="mb-1 mt-2" />
                        The fxrate was: €1.0000 = ${{ action.fx_rate }}
                        <!-- <pre>{{ action }}</pre> -->
                    </div>
                </div>
            </li>
        </ol>
    </div>
</template>

<script setup lang="ts">
import { defineComponent, onMounted, ref } from "vue";
import { api } from "../utils/api";

onMounted(() => {
    api.get("/stock-actions").then((res) => {
        stockActions.value = res.data.map((el: StockActions) => ({
            ...el,
            action: "Koop",
        }));
        console.log(stockActions.value);
    });
});

const stockActions = ref<StockActions[]>([]);

interface StockActions {
    order_id: string;
    share_id: string;
    quantity: number;
    transaction_cost: number;
    foreign_mutation: number;
    home_mutation: number;
    fx_rate: number;
    action: string;
}

interface Activity {
    time: string;
    content: string | JSX.Element;
}

const activities = ref<Activity[]>([
    {
        time: "just now",
        content:
            'Bonnie moved <a href="#" class="font-semibold text-blue-600 dark:text-blue-500 hover:underline">Jese Leos</a> to <span class="bg-gray-100 text-gray-800 text-xs font-normal me-2 px-2.5 py-0.5 rounded dark:bg-gray-600 dark:text-gray-300">Funny Group</span>',
    },
    {
        time: "2 hours ago",
        content:
            'Thomas Lean commented on <a href="#" class="font-semibold text-gray-900 dark:text-white hover:underline">Flowbite Pro</a>',
    },
    {
        time: "1 day ago",
        content:
            'Jese Leos has changed <a href="#" class="font-semibold text-blue-600 dark:text-blue-500 hover:underline">Pricing page</a> task status to <span class="font-semibold text-gray-900 dark:text-white">Finished</span>',
    },
]);
</script>
