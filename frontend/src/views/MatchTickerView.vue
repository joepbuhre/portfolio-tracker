<template>
    <button
        class="rounded-md border border-solid border-slate-600 bg-blue-700 px-2 py-1 text-white duration-200 hover:bg-opacity-80"
        @click="saveTickers"
    >
        Save tickers
    </button>
    <div class="flex md:px-32">
        <table class="min-w-full">
            <thead class="border-b bg-white">
                <tr>
                    <th
                        scope="col"
                        class="px-6 py-4 text-left text-sm font-medium text-gray-900"
                    >
                        ID
                    </th>
                    <th
                        scope="col"
                        class="px-6 py-4 text-left text-sm font-medium text-gray-900"
                    >
                        ISIN
                    </th>
                    <th
                        scope="col"
                        class="px-6 py-4 text-left text-sm font-medium text-gray-900"
                    >
                        Description
                    </th>
                    <th
                        scope="col"
                        class="px-6 py-4 text-left text-sm font-medium text-gray-900"
                    >
                        Market
                    </th>
                    <th
                        scope="col"
                        class="px-6 py-4 text-left text-sm font-medium text-gray-900"
                    >
                        Ticker
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr
                    v-for="row in res"
                    class="border-b odd:bg-gray-100 even:bg-white"
                >
                    <td
                        class="whitespace-nowrap px-6 py-4 text-sm font-medium text-gray-900"
                    >
                        {{ row.id }}
                    </td>
                    <td
                        class="whitespace-nowrap px-6 py-4 text-sm font-light text-gray-900"
                    >
                        {{ row.isin }}
                    </td>
                    <td
                        class="whitespace-nowrap px-6 py-4 text-sm font-light text-gray-900"
                    >
                        {{ row.description }}
                    </td>
                    <td
                        class="whitespace-nowrap px-6 py-4 text-sm font-light text-gray-900"
                    >
                        {{ row.market }}
                    </td>
                    <td
                        class="whitespace-nowrap px-6 py-4 text-sm font-light text-gray-900"
                    >
                        <input
                            v-model="changedShares[row.id]"
                            :name="row.id"
                            class="border-b border-b-black bg-transparent outline-none placeholder:text-gray-300"
                            placeholder="put in ticker"
                        />
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { api } from "../utils/api";

interface share_info {
    id: string;
    isin: string;
    description: string;
    market: string;
    ticker: string;
}

const res = ref<share_info[]>([]);

const changedShares = ref<{ [key: string]: string }>({});

onMounted(() => {
    api.get("/stocks").then((result) => {
        res.value = result.data;
        changedShares.value = Object.fromEntries(
            result.data.map((el: share_info) => [el.id, el.ticker]),
        );
    });
});

const saveTickers = () => {
    const saveObj = Object.entries(changedShares.value)
        .map((el) => ({
            share_id: el[0],
            ticker: el[1],
        }))
        .filter((el) => el.ticker !== null && el.ticker !== "");

    api.post("/match-ticker", saveObj)
        .then((res) => {
            alert("saved!");
        })
        .catch((err) => {
            alert(err.data);
        });
};
</script>
