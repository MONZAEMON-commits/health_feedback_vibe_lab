(() => {
  const groups = ["physical", "mental"];
  const absentCheckbox = document.querySelector('input[name="is_absent"]');

  function radiosByName(name) {
    return document.querySelectorAll(`input[name="${name}"][type="radio"]`);
  }

  function refreshActive(name) {
    const radios = radiosByName(name);
    radios.forEach((radio) => {
      const label = document.querySelector(`label[for="${radio.id}"]`);
      if (!label) return;
      label.classList.toggle("is-active", radio.checked);
      label.classList.toggle("is-disabled", radio.disabled);
    });
  }

  function addTapEffect(radio) {
    const label = document.querySelector(`label[for="${radio.id}"]`);
    if (!label || radio.disabled) return;
    label.classList.remove("is-tap");
    void label.offsetWidth;
    label.classList.add("is-tap");
  }

  function clearScores() {
    groups.forEach((name) => {
      radiosByName(name).forEach((radio) => {
        radio.checked = false;
      });
      refreshActive(name);
    });
  }

  function setScoresDisabled(disabled) {
    groups.forEach((name) => {
      radiosByName(name).forEach((radio) => {
        radio.disabled = disabled;
      });
      refreshActive(name);
    });
  }

  groups.forEach((name) => {
    const radios = radiosByName(name);
    radios.forEach((radio) => {
      radio.addEventListener("change", () => {
        // スコア選択時は「休み」を外す（排他制御）
        if (radio.checked && absentCheckbox && absentCheckbox.checked) {
          absentCheckbox.checked = false;
          setScoresDisabled(false);
        }
        refreshActive(name);
        addTapEffect(radio);
      });

      const label = document.querySelector(`label[for="${radio.id}"]`);
      if (label) {
        label.addEventListener("mouseenter", () => {
          if (!radio.checked && !radio.disabled) label.classList.add("is-active");
        });
        label.addEventListener("mouseleave", () => {
          if (!radio.checked) label.classList.remove("is-active");
        });
      }
    });
    refreshActive(name);
  });

  if (absentCheckbox) {
    absentCheckbox.addEventListener("change", () => {
      if (absentCheckbox.checked) {
        // 休み選択時はスコアをクリアして無効化
        clearScores();
        setScoresDisabled(true);
      } else {
        setScoresDisabled(false);
      }
    });

    // 初期表示時も状態を反映
    if (absentCheckbox.checked) {
      clearScores();
      setScoresDisabled(true);
    }
  }
})();
