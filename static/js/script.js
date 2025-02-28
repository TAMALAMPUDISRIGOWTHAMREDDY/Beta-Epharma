document.addEventListener("DOMContentLoaded", function () { 
    console.log("JavaScript Loaded");
    
    async function redirectToPharmacy(medicineName) {
        const encodedMedicine = encodeURIComponent(medicineName.trim());
        
        const pharmacies = {
            netmeds: {
                searchUrl: `https://www.netmeds.com/catalogsearch/result/${encodedMedicine}/all`,
                fallbackUrl: "https://www.netmeds.com/"
            },
            apollo: {
                searchUrl: `https://www.apollopharmacy.in/search-medicines/${encodedMedicine}`,
                fallbackUrl: "https://www.apollopharmacy.in/"
            },
            pharmeasy: {
                searchUrl: `https://pharmeasy.in/search/all?name=${encodedMedicine}`,
                fallbackUrl: "https://pharmeasy.in/"
            }
        };

        for (const key in pharmacies) {
            try {
                let response = await fetch(pharmacies[key].searchUrl, { method: 'HEAD' });
                if (response.ok) {
                    window.open(pharmacies[key].searchUrl, "_blank"); 
                } else {
                    window.open(pharmacies[key].fallbackUrl, "_blank");
                }
            } catch (error) {
                window.open(pharmacies[key].fallbackUrl, "_blank");
            }
        }
    }
    const start=document.getElementById("#Start");
    start.onclick=()=>{
        location.href="index.html";
    }
    // Form validation for symptoms search
    let form = document.querySelector("form");
    if (form) {
        form.addEventListener("submit", function (event) {
            let symptomsInput = document.querySelector("input[name='symptoms']");
            let ageInput = document.querySelector("input[name='age']");
            let genderInput = document.querySelector("select[name='Gender']");

            console.log("Debugging Form Input:");
            console.log("Symptoms:", symptomsInput ? symptomsInput.value.trim() : "Not Found");
            console.log("Age:", ageInput ? ageInput.value.trim() : "Not Found");
            console.log("Gender:", genderInput ? genderInput.value : "Not Found");

            if (!symptomsInput || symptomsInput.value.trim() === "") {
                alert("Please enter symptoms before searching for medicines.");
                event.preventDefault();
            } else if (!ageInput || ageInput.value.trim() === "" || isNaN(ageInput.value) || parseInt(ageInput.value) <= 0) {
                alert("Please enter a valid age.");
                event.preventDefault();
            } else if (!genderInput || genderInput.value === "") {
                alert("Please select your gender.");
                event.preventDefault();
            }
        });
    }
    // Image hover effect - Highlight emergency images
    let emergencyImages = document.querySelectorAll(".emergency img");
    emergencyImages.forEach(img => {
        img.addEventListener("mouseover", function () {
            this.style.transform = "scale(1.1)";
            this.style.transition = "transform 0.3s ease-in-out";
        });

        img.addEventListener("mouseout", function () {
            this.style.transform = "scale(1)";
        });
    });
});
