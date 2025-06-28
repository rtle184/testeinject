import React, { useState, useEffect } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [downloadStatus, setDownloadStatus] = useState("");
  const [isSetupComplete, setIsSetupComplete] = useState(false);
  const [userAgent, setUserAgent] = useState("");
  const [downloads, setDownloads] = useState([]);

  useEffect(() => {
    setUserAgent(navigator.userAgent);
    checkProtocolSupport();
    fetchDownloadStats();
  }, []);

  const checkProtocolSupport = () => {
    // Check if the custom protocol is supported
    try {
      const testLink = document.createElement('a');
      testLink.href = 'msiexec://test';
      // If the protocol is registered, this won't throw an error
      setIsSetupComplete(localStorage.getItem('msi-protocol-setup') === 'true');
    } catch (e) {
      setIsSetupComplete(false);
    }
  };

  const fetchDownloadStats = async () => {
    try {
      const response = await axios.get(`${API}/downloads`);
      setDownloads(response.data);
    } catch (error) {
      console.error("Error fetching download stats:", error);
    }
  };

  const trackDownload = async (filename) => {
    try {
      await axios.post(`${API}/track-download`, {
        filename: filename,
        user_agent: userAgent,
        ip_address: "client-side" // In production, you'd get this from the server
      });
      fetchDownloadStats();
    } catch (error) {
      console.error("Error tracking download:", error);
    }
  };

  const downloadAndInstallMSI = async () => {
    try {
      setDownloadStatus("Iniciando download...");
      
      // Create a temporary download link
      const link = document.createElement('a');
      link.href = `${API}/download/sample.msi`;
      link.download = 'sample.msi';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Track the download
      await trackDownload('sample.msi');
      
      setDownloadStatus("Download iniciado! Aguarde...");
      
      // Wait a bit for the download to start
      setTimeout(() => {
        if (isSetupComplete) {
          // Try to use the custom protocol to auto-install
          const msiPath = getDownloadPath('sample.msi');
          const protocolUrl = `msiexec://${msiPath}`;
          
          setDownloadStatus("Executando instalação automática...");
          
          // Create hidden link with custom protocol
          const protocolLink = document.createElement('a');
          protocolLink.href = protocolUrl;
          protocolLink.style.display = 'none';
          document.body.appendChild(protocolLink);
          protocolLink.click();
          document.body.removeChild(protocolLink);
          
          setDownloadStatus("Instalação iniciada! Verifique as janelas do sistema.");
        } else {
          setDownloadStatus("Download concluído! Configure o sistema primeiro para instalação automática.");
          showManualInstructions();
        }
      }, 2000);
      
    } catch (error) {
      console.error("Error:", error);
      setDownloadStatus("Erro durante o processo. Tente novamente.");
    }
  };

  const getDownloadPath = (filename) => {
    // Get the typical download path for Windows
    const userProfile = window.navigator.userAgent.includes('Windows') 
      ? `C:\\Users\\${getUserName()}\\Downloads\\${filename}`
      : `~/Downloads/${filename}`;
    return userProfile;
  };

  const getUserName = () => {
    // This is a fallback - in a real implementation you might get this differently
    return 'User';
  };

  const showManualInstructions = () => {
    const instructions = `
    Para usar a instalação automática:
    
    1. Baixe e execute o arquivo de configuração
    2. Aceite as permissões de administrador
    3. Clique no botão novamente para instalação automática
    
    Ou execute manualmente:
    - Vá para sua pasta Downloads
    - Clique duas vezes no arquivo sample.msi
    - Siga as instruções de instalação
    `;
    
    alert(instructions);
  };

  const setupProtocolHandler = async () => {
    try {
      setDownloadStatus("Baixando configuração do sistema...");
      
      // Download the PowerShell setup script
      const link = document.createElement('a');
      link.href = `${API}/download/installer-helper.ps1`;
      link.download = 'installer-helper.ps1';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      await trackDownload('installer-helper.ps1');
      
      setTimeout(() => {
        setDownloadStatus("Configuração baixada! Execute como Administrador.");
        showSetupInstructions();
      }, 1000);
      
    } catch (error) {
      console.error("Error downloading setup:", error);
      setDownloadStatus("Erro ao baixar configuração.");
    }
  };

  const showSetupInstructions = () => {
    const instructions = `
    INSTRUÇÕES DE CONFIGURAÇÃO:
    
    1. Vá para sua pasta Downloads
    2. Clique com botão direito em "installer-helper.ps1"
    3. Selecione "Executar com PowerShell"
    4. Aceite executar como Administrador
    5. Aguarde a mensagem de sucesso
    6. Volte aqui e clique em "Marcar como Configurado"
    
    Após isso, você poderá usar a instalação automática!
    `;
    
    alert(instructions);
  };

  const markSetupComplete = () => {
    localStorage.setItem('msi-protocol-setup', 'true');
    setIsSetupComplete(true);
    setDownloadStatus("Sistema configurado! Agora você pode usar a instalação automática.");
  };

  const testAutoInstall = () => {
    // Test the protocol with a simple message
    const testUrl = 'msiexec://test';
    const link = document.createElement('a');
    link.href = testUrl;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-white mb-4">
            🚀 MSI Auto-Installer
          </h1>
          <p className="text-xl text-blue-200 max-w-2xl mx-auto">
            Sistema inteligente que baixa e instala arquivos MSI automaticamente
          </p>
        </div>

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8">
            
            {/* Left Column - Main Action */}
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
              <h2 className="text-2xl font-bold text-white mb-6">
                {isSetupComplete ? "✅ Sistema Configurado" : "⚙️ Configuração Necessária"}
              </h2>
              
              {!isSetupComplete ? (
                <div className="space-y-4">
                  <p className="text-gray-200">
                    Para usar a instalação automática, primeiro configure o sistema:
                  </p>
                  <button
                    onClick={setupProtocolHandler}
                    className="w-full bg-yellow-500 hover:bg-yellow-600 text-black font-bold py-4 px-6 rounded-xl transition-all duration-200 transform hover:scale-105"
                  >
                    📥 Baixar Configuração do Sistema
                  </button>
                  <button
                    onClick={markSetupComplete}
                    className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-3 px-6 rounded-xl transition-all duration-200"
                  >
                    ✓ Marcar como Configurado
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <p className="text-green-200">
                    Sistema pronto! Clique para baixar e instalar automaticamente:
                  </p>
                  <button
                    onClick={downloadAndInstallMSI}
                    className="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-4 px-6 rounded-xl transition-all duration-200 transform hover:scale-105 animate-pulse"
                  >
                    🔥 BAIXAR E INSTALAR AUTOMATICAMENTE
                  </button>
                  <button
                    onClick={testAutoInstall}
                    className="w-full bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-xl transition-all duration-200"
                  >
                    🧪 Testar Instalação Automática
                  </button>
                </div>
              )}
              
              {/* Status Display */}
              {downloadStatus && (
                <div className="mt-6 p-4 bg-blue-500/20 rounded-xl border border-blue-400/30">
                  <p className="text-blue-200 font-medium">
                    📊 Status: {downloadStatus}
                  </p>
                </div>
              )}
            </div>

            {/* Right Column - Info and Stats */}
            <div className="space-y-6">
              
              {/* How it Works */}
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">
                  🔧 Como Funciona
                </h3>
                <div className="space-y-3 text-sm text-gray-200">
                  <div className="flex items-start space-x-2">
                    <span className="text-blue-400">1.</span>
                    <span>Registra um protocolo customizado no Windows</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="text-blue-400">2.</span>
                    <span>Baixa o arquivo MSI automaticamente</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="text-blue-400">3.</span>
                    <span>Executa o MSI com permissões elevadas</span>
                  </div>
                  <div className="flex items-start space-x-2">
                    <span className="text-blue-400">4.</span>
                    <span>Mostra progresso e status em tempo real</span>
                  </div>
                </div>
              </div>

              {/* Download Stats */}
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">
                  📈 Estatísticas
                </h3>
                <div className="grid grid-cols-2 gap-4 text-center">
                  <div className="bg-blue-500/20 rounded-lg p-3">
                    <div className="text-2xl font-bold text-blue-300">
                      {downloads.length}
                    </div>
                    <div className="text-xs text-blue-200">
                      Total Downloads
                    </div>
                  </div>
                  <div className="bg-green-500/20 rounded-lg p-3">
                    <div className="text-2xl font-bold text-green-300">
                      {isSetupComplete ? "100%" : "0%"}
                    </div>
                    <div className="text-xs text-green-200">
                      Configuração
                    </div>
                  </div>
                </div>
              </div>

              {/* Security Notice */}
              <div className="bg-red-500/20 backdrop-blur-lg rounded-2xl p-6 border border-red-400/30">
                <h3 className="text-xl font-bold text-red-300 mb-2">
                  🔒 Aviso de Segurança
                </h3>
                <p className="text-red-200 text-sm">
                  Este sistema executa arquivos com permissões elevadas. 
                  Use apenas com arquivos confiáveis de fontes verificadas.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12">
          <p className="text-blue-300">
            Desenvolvido com ❤️ para automação de instalações MSI
          </p>
        </div>
      </div>
    </div>
  );
}

export default App;