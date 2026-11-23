    afterLanding(() => {
        try {
            initCodeExplains();
        } catch (error) {
            console.error(error);
        }
    });
})();
