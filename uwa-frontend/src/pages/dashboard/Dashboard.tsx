import { useNavigate } from "react-router-dom";
import { getFirebaseAuth } from "../../firebase/firebaseAuth";
import { signOut } from "firebase/auth";
import { useEffect } from "react";


export default function Dashboard() {
    const navigate = useNavigate();

    async function signOutUser() {
        await signOut(getFirebaseAuth())
        navigate("/", { replace: true });
    }

    const user = getFirebaseAuth().currentUser;

    useEffect(() => {
        if (user && !user.emailVerified) {
            alert(
                "Please verify your email before logging in. App will refuse to work without a verified email."
            );

            signOutUser();
        }
    }, [user]);

    return <>
        Dashboard!
        <button onClick={signOutUser}>Sign out</button> 
    </>
}