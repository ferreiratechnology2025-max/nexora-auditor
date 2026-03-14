import { Award, Download, Share2, QrCode, CheckCircle, TrendingUp } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useState } from 'react';
import { useLocation } from 'wouter';

export default function Certifications() {
  const [selectedCert, setSelectedCert] = useState<number | null>(null);
  const [, setLocation] = useLocation();

  const certificates = [
    {
      id: 1,
      projectName: 'E-commerce Platform',
      score: 92,
      date: '2026-03-10',
      category: 'Segurança',
      vulnerabilities: { critical: 0, high: 2, medium: 5 },
      qrCode: 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://auditx.com/v/cert-001',
      certId: 'AUDITX-2026-001'
    },
    {
      id: 2,
      projectName: 'Mobile App Backend',
      score: 87,
      date: '2026-03-09',
      category: 'Performance',
      vulnerabilities: { critical: 0, high: 1, medium: 8 },
      qrCode: 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://auditx.com/v/cert-002',
      certId: 'AUDITX-2026-002'
    },
    {
      id: 3,
      projectName: 'API Gateway',
      score: 95,
      date: '2026-03-08',
      category: 'Segurança',
      vulnerabilities: { critical: 0, high: 0, medium: 3 },
      qrCode: 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://auditx.com/v/cert-003',
      certId: 'AUDITX-2026-003'
    },
    {
      id: 4,
      projectName: 'Data Pipeline',
      score: 78,
      date: '2026-03-07',
      category: 'Qualidade',
      vulnerabilities: { critical: 1, high: 3, medium: 12 },
      qrCode: 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://auditx.com/v/cert-004',
      certId: 'AUDITX-2026-004'
    },
    {
      id: 5,
      projectName: 'Admin Dashboard',
      score: 88,
      date: '2026-03-06',
      category: 'Segurança',
      vulnerabilities: { critical: 0, high: 2, medium: 6 },
      qrCode: 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://auditx.com/v/cert-005',
      certId: 'AUDITX-2026-005'
    },
    {
      id: 6,
      projectName: 'Payment Processor',
      score: 96,
      date: '2026-03-05',
      category: 'Segurança',
      vulnerabilities: { critical: 0, high: 0, medium: 2 },
      qrCode: 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=https://auditx.com/v/cert-006',
      certId: 'AUDITX-2026-006'
    }
  ];

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-safe';
    if (score >= 75) return 'text-warning';
    return 'text-critical';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 90) return 'bg-safe/10';
    if (score >= 75) return 'bg-warning/10';
    return 'bg-critical/10';
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-b from-slate-50 to-white border-b border-border">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl sm:text-5xl font-bold font-mono text-foreground mb-4">
              Certificações
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              Laudos auditados com score certificado, QR Code verificável e timestamp. Compartilhe com confiança.
            </p>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-slate-50 border-b border-border">
        <div className="max-w-6xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="bg-white border border-border rounded-lg p-6 text-center">
              <div className="text-3xl font-bold text-primary font-mono mb-2">1,247</div>
              <p className="text-muted-foreground">Projetos Auditados</p>
            </div>
            <div className="bg-white border border-border rounded-lg p-6 text-center">
              <div className="text-3xl font-bold text-primary font-mono mb-2">94%</div>
              <p className="text-muted-foreground">Média de Score</p>
            </div>
            <div className="bg-white border border-border rounded-lg p-6 text-center">
              <div className="text-3xl font-bold text-safe font-mono mb-2">8,942</div>
              <p className="text-muted-foreground">Vulnerabilidades Fixadas</p>
            </div>
            <div className="bg-white border border-border rounded-lg p-6 text-center">
              <div className="text-3xl font-bold text-primary font-mono mb-2">100%</div>
              <p className="text-muted-foreground">Verificáveis</p>
            </div>
          </div>
        </div>
      </section>

      {/* Certificates Gallery */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold font-mono text-foreground mb-12">
            Certificados Recentes
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {certificates.map((cert) => (
              <div
                key={cert.id}
                className="bg-white border border-border rounded-lg overflow-hidden hover:shadow-lg transition-shadow duration-300 cursor-pointer"
                onClick={() => setSelectedCert(selectedCert === cert.id ? null : cert.id)}
              >
                {/* Card Header */}
                <div className={`p-6 ${getScoreBgColor(cert.score)}`}>
                  <div className="flex items-start justify-between mb-4">
                    <div>
                      <h3 className="text-lg font-bold text-foreground mb-1">
                        {cert.projectName}
                      </h3>
                      <p className="text-sm text-muted-foreground">{cert.certId}</p>
                    </div>
                    <Award className="w-6 h-6 text-primary flex-shrink-0" />
                  </div>
                </div>

                {/* Card Body */}
                <div className="p-6">
                  {/* Score */}
                  <div className="flex items-center justify-between mb-6">
                    <span className="text-muted-foreground">Score</span>
                    <span className={`text-3xl font-bold font-mono ${getScoreColor(cert.score)}`}>
                      {cert.score}
                    </span>
                  </div>

                  {/* Vulnerabilities */}
                  <div className="mb-6 space-y-2">
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-critical font-medium">Críticas: {cert.vulnerabilities.critical}</span>
                      {cert.vulnerabilities.critical === 0 && <CheckCircle className="w-4 h-4 text-safe" />}
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-warning font-medium">Altas: {cert.vulnerabilities.high}</span>
                      {cert.vulnerabilities.high <= 1 && <CheckCircle className="w-4 h-4 text-safe" />}
                    </div>
                    <div className="flex justify-between items-center text-sm">
                      <span className="text-muted-foreground">Médias: {cert.vulnerabilities.medium}</span>
                    </div>
                  </div>

                  {/* Date and Category */}
                  <div className="flex justify-between items-center mb-6 pb-6 border-b border-border">
                    <span className="text-sm text-muted-foreground">{cert.date}</span>
                    <span className="text-xs font-semibold px-3 py-1 bg-primary/10 text-primary rounded-full">
                      {cert.category}
                    </span>
                  </div>

                  {/* Expanded Content */}
                  {selectedCert === cert.id && (
                    <div className="mb-6 pb-6 border-b border-border">
                      <div className="flex justify-center mb-4">
                        <img
                          src={cert.qrCode}
                          alt={`QR Code verificável do certificado ${cert.certId} para ${cert.projectName}`}
                          className="w-32 h-32 border border-border rounded"
                          width="200"
                          height="200"
                          loading="lazy"
                        />
                      </div>
                      <p className="text-xs text-muted-foreground text-center mb-4">
                        Escaneie para verificar o laudo público
                      </p>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" className="flex-1">
                      <Download className="w-4 h-4 mr-2" />
                      PDF
                    </Button>
                    <Button variant="outline" size="sm" className="flex-1">
                      <Share2 className="w-4 h-4 mr-2" />
                      Compartilhar
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Verification Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-slate-50 border-t border-border">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold font-mono text-foreground mb-12 text-center">
            Como Verificar um Certificado
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="bg-white border border-border rounded-lg p-8 text-center">
              <QrCode className="w-12 h-12 text-primary mx-auto mb-4" />
              <h3 className="font-bold text-foreground mb-2">1. Escaneie o QR Code</h3>
              <p className="text-sm text-muted-foreground">
                Use qualquer leitor de QR Code para acessar o laudo público
              </p>
            </div>

            <div className="bg-white border border-border rounded-lg p-8 text-center">
              <TrendingUp className="w-12 h-12 text-primary mx-auto mb-4" />
              <h3 className="font-bold text-foreground mb-2">2. Verifique o Score</h3>
              <p className="text-sm text-muted-foreground">
                Confirme o score certificado com timestamp e assinatura digital
              </p>
            </div>

            <div className="bg-white border border-border rounded-lg p-8 text-center">
              <CheckCircle className="w-12 h-12 text-safe mx-auto mb-4" />
              <h3 className="font-bold text-foreground mb-2">3. Confie no Resultado</h3>
              <p className="text-sm text-muted-foreground">
                Cada certificado é único e imutável. Impossível falsificar.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold font-mono text-foreground mb-12 text-center">
            Perguntas Frequentes
          </h2>

          <div className="space-y-6">
            {[
              {
                q: 'Quanto tempo um certificado é válido?',
                a: 'Os certificados são permanentes e imutáveis. O QR Code e o link público funcionam indefinidamente, permitindo que você compartilhe com clientes a qualquer momento.'
              },
              {
                q: 'Posso compartilhar o certificado com meus clientes?',
                a: 'Sim! Cada certificado tem um link público único com QR Code. Compartilhe via e-mail, WhatsApp ou qualquer canal. Seus clientes podem verificar a autenticidade do laudo.'
              },
              {
                q: 'O certificado prova que o código é 100% seguro?',
                a: 'O certificado prova que o código foi auditado com sucesso e que as vulnerabilidades detectadas foram corrigidas. Nenhum código é 100% seguro, mas o AUDITX garante que as vulnerabilidades conhecidas foram eliminadas.'
              },
              {
                q: 'Posso usar o certificado em marketing?',
                a: 'Sim! O certificado com QR Code verificável é ótimo para marketing. Seus clientes podem escanear e confirmar que o código foi auditado e aprovado.'
              }
            ].map((faq, idx) => (
              <div key={idx} className="bg-white border border-border rounded-lg p-8">
                <h3 className="font-bold text-foreground mb-3">{faq.q}</h3>
                <p className="text-muted-foreground">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-primary/10 to-primary/5 border-t border-border">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold font-mono text-foreground mb-6">
            Obtenha Seu Certificado Hoje
          </h2>
          <p className="text-lg text-muted-foreground mb-8">
            Audite seu projeto e receba um certificado verificável com QR Code.
          </p>
          <Button size="lg" variant="default" onClick={() => setLocation('/')}>
            Começar Auditoria
          </Button>
        </div>
      </section>
    </div>
  );
}
