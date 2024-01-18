import axios, {
    AxiosError,
    AxiosRequestConfig,
    AxiosResponse,
    InternalAxiosRequestConfig,
} from "axios";
import { useMain } from "../store/main";
import { useNotifications } from "@src/store/notifications";
import { NotificationType } from "@src/enums/Notification";

export const api = axios.create({
    baseURL: import.meta.env.DEV ? "http://localhost:8000" : "/",
});

api.interceptors.request.use(
    (conf: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
        const main = useMain();
        main.setLoading(true);
        if (conf.headers.get("x-userid") === undefined && main.getUserId) {
            conf.headers.set("x-userid", main.getUserId);
        }
        return conf;
    },
);

api.interceptors.response.use(
    (res: AxiosResponse): AxiosResponse => {
        const main = useMain();
        main.setLoading(false);
        return res;
    },
    (error: AxiosError) => {
        const main = useMain();
        main.setLoading(false);
        error.message = (<any>error.response?.data)?.detail ?? error.message;

        const not = useNotifications();
        not.add(error.message, NotificationType.Error);

        return Promise.reject(error);
    },
);
