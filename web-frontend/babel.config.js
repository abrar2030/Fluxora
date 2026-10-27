// Vite exposes build-time variables through import.meta.env, which Jest's
// CommonJS runtime cannot parse. For tests only, rewrite `import.meta` to an
// object whose `env` is process.env.
const importMetaToProcessEnv = ({ types: t }) => ({
  name: "import-meta-to-process-env",
  visitor: {
    MetaProperty(path) {
      if (
        path.node.meta.name === "import" &&
        path.node.property.name === "meta"
      ) {
        path.replaceWith(
          t.objectExpression([
            t.objectProperty(
              t.identifier("env"),
              t.memberExpression(t.identifier("process"), t.identifier("env")),
            ),
          ]),
        );
      }
    },
  },
});

module.exports = (api) => {
  const isTest = api.env("test");
  return {
    presets: [
      ["@babel/preset-env", { targets: { node: "current" } }],
      ["@babel/preset-react", { runtime: "automatic" }],
    ],
    plugins: isTest ? [importMetaToProcessEnv] : [],
  };
};
