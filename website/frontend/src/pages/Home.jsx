import Navbar from "../components/Navbar";
import Hero from "../components/Hero";
import CodeExample from "../components/CodeExample";
import WhyPulse from "../components/WhyPulse";
import Features from "../components/Features";
import ArchitectureOverview from "../components/ArchitectureOverview";
import Footer from "../components/Footer";

function Home() {
    return (
        <>
            <Navbar />
            <Hero />
            <CodeExample />
            <WhyPulse />
            <Features />
            <ArchitectureOverview />
            <Footer />
        </>
    )
}

export default Home
