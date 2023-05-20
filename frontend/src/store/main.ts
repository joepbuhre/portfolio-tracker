import { defineStore } from "pinia";

interface stateType {
    loading: boolean,
    loadingLock: string | null,
    userid: string | null
}

export const useMain = defineStore("Main", {
    state(): stateType {
        return {
            loading: false,
            loadingLock: null,
            userid: null,
        };
    },
    getters: {
        isLoading(state): boolean {
            return state.loading
        },
        getUserId(state): string | null { 
            return state.userid
        }
    },
    actions: {
        setLoading(modus: boolean | null = null, lock: string | null = null) {
            if(this.loadingLock === null && lock !== null) {
                this.loadingLock = lock     
            }
            if(this.loadingLock !== null && this.loadingLock !== lock) {
                return false;
            } else {   
                if(modus === null) {
                    this.loading = !this.loading
                } else {
                    this.loading = modus
                }
                this.loadingLock = null
            }
        },
        setUserId(uuid: string | null) {
            this.userid = uuid
        }
    },
    persist: true
});