(() => {
  const groups = ["physical", "mental"];

  function refreshActive(name) {
    const radios = document.querySelectorAll(`input[name="${name}"][type="radio"]`);
    radios.forEach((radio) => {
      const label = document.querySelector(`label[for="${radio.id}"]`);
      if (!label) return;
      label.classList.toggle("is-active", radio.checked);
    });
  }

  function addTapEffect(radio) {
    const label = document.querySelector(`label[for="${radio.id}"]`);
    if (!label) return;
    label.classList.remove("is-tap");
    void label.offsetWidth;
    label.classList.add("is-tap");
  }

  groups.forEach((name) => {
    const radios = document.querySelectorAll(`input[name="${name}"][type="radio"]`);
    radios.forEach((radio) => {
      radio.addEventListener("change", () => {
        refreshActive(name);
        addTapEffect(radio);
      });
      const label = document.querySelector(`label[for="${radio.id}"]`);
      if (label) {
        label.addEventListener("mouseenter", () => {
          if (!radio.checked) label.classList.add("is-active");
        });
        label.addEventListener("mouseleave", () => {
          if (!radio.checked) label.classList.remove("is-active");
        });
      }
    });
    refreshActive(name);
  });
})();
